from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import logging
import os
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from collections.abc import Mapping, Sequence
import math
import sys

# Add ML_models to path
sys.path.append(str(Path(__file__).parent / "ML_models"))
from categories_knn import knn_predict, load_model
from find_subscriptions import load_model as load_subscription_model, predict_subscriptions

# Add LLM to path
sys.path.append(str(Path(__file__).parent / "llm"))
from llm_insights import generate_llm_cards


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Financial Coach API",
    description="API for processing financial transaction CSV files with ML-powered categorization",
    version="1.0.0"
)

# Initialize ML models on startup
@app.on_event("startup")
async def startup_event():
    """Initialize ML models when the application starts"""
    initialize_ml_model()
    initialize_subscription_model()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("transaction_data")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create hash registry file to track file hashes
HASH_REGISTRY_FILE = UPLOAD_DIR / "file_hashes.json"

# ML Model initialization
ML_MODEL_LOADED = False
ML_MODEL_PATH = Path(__file__).parent / "ML_models" / "knn_model.joblib"

SUBSCRIPTION_MODEL_LOADED = False
SUBSCRIPTION_MODEL_PATH = Path(__file__).parent / "ML_models" / "subscriptions_v1.joblib"
SUBSCRIPTION_COLS_PATH = Path(__file__).parent / "ML_models" / "subscriptions_v1.cols.json"
SUBSCRIPTION_MODEL = None
SUBSCRIPTION_FEATURE_COLS = None

# Subscription merchant to website mapping
SUBSCRIPTION_WEBSITES = {
    # Streaming Services
    "NETFLIX": "https://netflix.com",
    "SPOTIFY": "https://spotify.com",
    "AMAZON PRIME": "https://amazon.com/prime",
    "DISNEY": "https://disneyplus.com",
    "HULU": "https://hulu.com",
    "APPLE MUSIC": "https://music.apple.com",
    "YOUTUBE PREMIUM": "https://youtube.com/premium",
    "HBO MAX": "https://hbomax.com",
    "PARAMOUNT": "https://paramountplus.com",
    "PEACOCK": "https://peacocktv.com",
    
    # Software & Productivity
    "ADOBE": "https://adobe.com",
    "MICROSOFT 365": "https://microsoft.com/microsoft-365",
    "GOOGLE DRIVE": "https://drive.google.com",
    "DROPBOX": "https://dropbox.com",
    "NOTION": "https://notion.so",
    "SLACK": "https://slack.com",
    "ZOOM": "https://zoom.us",
    "CANVA": "https://canva.com",
    "FIGMA": "https://figma.com",
    
    # Gaming
    "XBOX": "https://xbox.com",
    "PLAYSTATION": "https://playstation.com",
    "STEAM": "https://store.steampowered.com",
    "NINTENDO": "https://nintendo.com",
    "EPIC GAMES": "https://epicgames.com",
    
    # Fitness & Health
    "PELOTON": "https://onepeloton.com",
    "CLASSPASS": "https://classpass.com",
    "MYFITNESSPAL": "https://myfitnesspal.com",
    "HEADSPACE": "https://headspace.com",
    "CALM": "https://calm.com",
    
    # Food & Delivery
    "UBER EATS": "https://ubereats.com",
    "DOORDASH": "https://doordash.com",
    "GRUBHUB": "https://grubhub.com",
    "INSTACART": "https://instacart.com",
    "HELLOFRESH": "https://hellofresh.com",
    "BLUE APRON": "https://blueapron.com",
    
    # Cloud & Hosting
    "AWS": "https://aws.amazon.com",
    "GOOGLE CLOUD": "https://cloud.google.com",
    "DIGITALOCEAN": "https://digitalocean.com",
    "HEROKU": "https://heroku.com",
    "NETLIFY": "https://netlify.com",
    
    # News & Media
    "NEW YORK TIMES": "https://nytimes.com",
    "WALL STREET JOURNAL": "https://wsj.com",
    "THE ATLANTIC": "https://theatlantic.com",
    "MEDIUM": "https://medium.com",
    "SUBSTACK": "https://substack.com",
    
    # Other Services
    "ICLOUD": "https://icloud.com",
    "ONEDRIVE": "https://onedrive.live.com",
    "LASTPASS": "https://lastpass.com",
    "1PASSWORD": "https://1password.com",
    "GRAMMARLY": "https://grammarly.com",
    "LINKEDIN": "https://linkedin.com/premium",
    "CRUNCHYROLL": "https://crunchyroll.com",
    "PATREON": "https://patreon.com",
    "ONLYFANS": "https://onlyfans.com",
    "TWITCH": "https://twitch.tv",
    "DISCORD": "https://discord.com",
    "TELEGRAM": "https://telegram.org",
    "SIGNAL": "https://signal.org"
}

# Expected financial transaction columns (flexible - will auto-detect)
EXPECTED_FINANCIAL_COLUMNS = [
    'date', 'description', 'amount', 'category', 'account', 'type',
    'transaction_date', 'merchant', 'debit', 'credit', 'balance'
]


def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of file content"""
    return hashlib.sha256(content).hexdigest()

def load_hash_registry() -> Dict[str, Dict[str, Any]]:
    """Load the hash registry from file"""
    if HASH_REGISTRY_FILE.exists():
        try:
            with open(HASH_REGISTRY_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load hash registry: {e}")
            return {}
    return {}

def save_hash_registry(registry: Dict[str, Dict[str, Any]]) -> None:
    """Save the hash registry to file"""
    try:
        with open(HASH_REGISTRY_FILE, 'w') as f:
            json.dump(registry, f, indent=2)
    except IOError as e:
        logger.error(f"Could not save hash registry: {e}")

def register_file_hash(file_hash: str, file_id: str, filename: str) -> None:
    """Register a file hash in the registry"""
    registry = load_hash_registry()
    registry[file_hash] = {
        "file_id": file_id,
        "filename": filename,
        "upload_time": datetime.now().isoformat()
    }
    save_hash_registry(registry)

def find_duplicate_file(file_hash: str) -> Optional[Dict[str, Any]]:
    """Check if a file with the same hash already exists"""
    registry = load_hash_registry()
    return registry.get(file_hash)

def initialize_ml_model():
    """Initialize the ML model for category prediction"""
    global ML_MODEL_LOADED
    try:
        if ML_MODEL_PATH.exists():
            load_model()
            ML_MODEL_LOADED = True
            logger.info("✅ ML model loaded successfully")
        else:
            logger.warning(f"⚠️ ML model not found at {ML_MODEL_PATH}")
            ML_MODEL_LOADED = False
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {e}")
        ML_MODEL_LOADED = False

def initialize_subscription_model():
    """Initialize the subscription detection model"""
    global SUBSCRIPTION_MODEL_LOADED, SUBSCRIPTION_MODEL, SUBSCRIPTION_FEATURE_COLS
    
    try:
        if SUBSCRIPTION_MODEL_PATH.exists() and SUBSCRIPTION_COLS_PATH.exists():
            SUBSCRIPTION_MODEL, SUBSCRIPTION_FEATURE_COLS = load_subscription_model(
                str(SUBSCRIPTION_MODEL_PATH), str(SUBSCRIPTION_COLS_PATH)
            )
            SUBSCRIPTION_MODEL_LOADED = True
            logger.info("✅ Subscription model loaded successfully")
        else:
            logger.warning(f"⚠️ Subscription model files not found")
            SUBSCRIPTION_MODEL_LOADED = False
    except Exception as e:
        logger.error(f"❌ Failed to load subscription model: {e}")
        SUBSCRIPTION_MODEL_LOADED = False

def find_subscription_website(merchant_name: str) -> Optional[str]:
    """
    Find the website URL for a subscription merchant name.
    Uses fuzzy matching to handle variations in merchant names.
    """
    if not merchant_name:
        return None
    
    # Normalize the merchant name for comparison
    normalized_name = merchant_name.upper().strip()
    
    # Direct match first
    if normalized_name in SUBSCRIPTION_WEBSITES:
        return SUBSCRIPTION_WEBSITES[normalized_name]
    
    # Fuzzy matching for common variations
    for known_merchant, website in SUBSCRIPTION_WEBSITES.items():
        # Check if the merchant name contains any of the known keywords
        if any(keyword in normalized_name for keyword in known_merchant.split()):
            return website
        
        # Check if any keyword from the merchant name matches known merchants
        merchant_words = normalized_name.split()
        for word in merchant_words:
            if word in known_merchant:
                return website
    
    # Special cases for common variations
    variations = {
        "NETFLIX": ["NETFLIX", "NETFLIX.COM"],
        "SPOTIFY": ["SPOTIFY", "SPOTIFY.COM"],
        "AMAZON": ["AMAZON", "AMAZON.COM", "AMAZON PRIME", "PRIME"],
        "DISNEY": ["DISNEY", "DISNEY+", "DISNEY PLUS"],
        "APPLE": ["APPLE", "APPLE MUSIC", "APPLE.COM"],
        "GOOGLE": ["GOOGLE", "GOOGLE DRIVE", "GOOGLE.COM"],
        "MICROSOFT": ["MICROSOFT", "MSFT", "OFFICE 365", "MICROSOFT 365"],
        "ADOBE": ["ADOBE", "ADOBE.COM"],
        "XBOX": ["XBOX", "XBOX LIVE"],
        "PLAYSTATION": ["PLAYSTATION", "PSN", "PLAYSTATION NETWORK"],
        "STEAM": ["STEAM", "STEAM.COM"],
        "UBER": ["UBER", "UBER EATS"],
        "DOORDASH": ["DOORDASH", "DOOR DASH"],
        "GRUBHUB": ["GRUBHUB", "GRUB HUB"],
        "INSTACART": ["INSTACART", "INSTA CART"],
        "HELLOFRESH": ["HELLOFRESH", "HELLO FRESH"],
        "BLUEAPRON": ["BLUEAPRON", "BLUE APRON"],
        "PELOTON": ["PELOTON", "PELOTON.COM"],
        "CLASSPASS": ["CLASSPASS", "CLASS PASS"],
        "MYFITNESSPAL": ["MYFITNESSPAL", "MY FITNESS PAL"],
        "HEADSPACE": ["HEADSPACE", "HEAD SPACE"],
        "NEW YORK TIMES": ["NYTIMES", "NEW YORK TIMES", "NY TIMES"],
        "WALL STREET JOURNAL": ["WSJ", "WALL STREET JOURNAL"],
        "THE ATLANTIC": ["ATLANTIC", "THE ATLANTIC"],
        "SUBSTACK": ["SUBSTACK", "SUB STACK"],
        "ONLYFANS": ["ONLYFANS", "ONLY FANS"],
        "CRUNCHYROLL": ["CRUNCHYROLL", "CRUNCHY ROLL"],
        "PATREON": ["PATREON", "PATREON.COM"],
        "TWITCH": ["TWITCH", "TWITCH.TV"],
        "DISCORD": ["DISCORD", "DISCORD.COM"],
        "TELEGRAM": ["TELEGRAM", "TELEGRAM.ORG"],
        "SIGNAL": ["SIGNAL", "SIGNAL.ORG"],
        "GRAMMARLY": ["GRAMMARLY", "GRAMMARLY.COM"],
        "LINKEDIN": ["LINKEDIN", "LINKEDIN.COM"],
        "LASTPASS": ["LASTPASS", "LAST PASS"],
        "1PASSWORD": ["1PASSWORD", "1 PASSWORD"],
        "ICLOUD": ["ICLOUD", "I CLOUD"],
        "ONEDRIVE": ["ONEDRIVE", "ONE DRIVE"],
        "AWS": ["AWS", "AMAZON WEB SERVICES"],
        "GOOGLE CLOUD": ["GOOGLE CLOUD", "GCP"],
        "DIGITALOCEAN": ["DIGITALOCEAN", "DIGITAL OCEAN"],
        "HEROKU": ["HEROKU", "HEROKU.COM"],
        "NETLIFY": ["NETLIFY", "NETLIFY.COM"],
        "DROPBOX": ["DROPBOX", "DROPBOX.COM"],
        "NOTION": ["NOTION", "NOTION.SO"],
        "SLACK": ["SLACK", "SLACK.COM"],
        "ZOOM": ["ZOOM", "ZOOM.US"],
        "CANVA": ["CANVA", "CANVA.COM"],
        "FIGMA": ["FIGMA", "FIGMA.COM"],
        "EPIC GAMES": ["EPIC", "EPIC GAMES"],
        "NINTENDO": ["NINTENDO", "NINTENDO.COM"],
        "HULU": ["HULU", "HULU.COM"],
        "HBO MAX": ["HBO", "HBO MAX", "MAX"],
        "PARAMOUNT": ["PARAMOUNT", "PARAMOUNT PLUS"],
        "PEACOCK": ["PEACOCK", "PEACOCK TV"],
        "YOUTUBE": ["YOUTUBE", "YOUTUBE PREMIUM"],
        "MEDIUM": ["MEDIUM", "MEDIUM.COM"]
    }
    
    for known_merchant, variation_list in variations.items():
        if any(variation in normalized_name for variation in variation_list):
            return SUBSCRIPTION_WEBSITES.get(known_merchant)
    
    return None

def predict_transaction_category(description: str, k: int = 5, threshold: float = 0.35) -> Tuple[str, float]:
    """
    Predict category for a transaction description using k-NN model
    
    Args:
        description: Transaction description text
        k: Number of neighbors to consider
        threshold: Minimum confidence threshold
        
    Returns:
        Tuple of (predicted_category, confidence_score)
    """
    if not ML_MODEL_LOADED:
        return "Uncategorized", 0.0
    
    try:
        return knn_predict(description, k=k, threshold=threshold)
    except Exception as e:
        logger.error(f"Error predicting category for '{description}': {e}")
        return "Uncategorized", 0.0

def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ML-predicted categories to transaction dataframe
    Separates income and spending transactions before ML categorization
    
    Args:
        df: DataFrame with transaction data
        
    Returns:
        DataFrame with added 'ml_category' and 'ml_confidence' columns
    """
    if not ML_MODEL_LOADED:
        logger.warning("ML model not loaded, skipping categorization")
        df['ml_category'] = 'Uncategorized'
        df['ml_confidence'] = 0.0
        return df
    
    # Find amount column
    amount_col = None
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['amount', 'debit', 'credit', 'value']):
            amount_col = col
            break
    
    # Find description column
    description_col = None
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['description', 'merchant', 'memo', 'details']):
            description_col = col
            break
    
    if description_col is None:
        logger.warning("No description column found for categorization")
        df['ml_category'] = 'Uncategorized'
        df['ml_confidence'] = 0.0
        return df
    
    # Initialize category and confidence columns
    df['ml_category'] = 'Uncategorized'
    df['ml_confidence'] = 0.0
    
    # Convert amount column to numeric for proper filtering
    if amount_col:
        df[amount_col] = pd.to_numeric(df[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
        
        # Separate income (positive amounts) and spending (negative amounts)
        income_mask = df[amount_col] > 0
        spending_mask = df[amount_col] <= 0
        
        # Automatically categorize income transactions
        df.loc[income_mask, 'ml_category'] = 'Income'
        df.loc[income_mask, 'ml_confidence'] = 1.0  # High confidence for income
        
        # Use ML model only for spending transactions
        spending_transactions = df[spending_mask]
        if len(spending_transactions) > 0:
            spending_categories = []
            spending_confidences = []
            
            for desc in spending_transactions[description_col].fillna(''):
                category, confidence = predict_transaction_category(str(desc))
                spending_categories.append(category)
                spending_confidences.append(confidence)
            
            # Update spending transactions with ML predictions
            df.loc[spending_mask, 'ml_category'] = spending_categories
            df.loc[spending_mask, 'ml_confidence'] = spending_confidences
    else:
        # If no amount column, use ML for all transactions (fallback)
        logger.warning("No amount column found, using ML for all transactions")
        categories = []
        confidences = []
        
        for desc in df[description_col].fillna(''):
            category, confidence = predict_transaction_category(str(desc))
            categories.append(category)
            confidences.append(confidence)
        
        df['ml_category'] = categories
        df['ml_confidence'] = confidences
    
    return df


def sanitize(obj):
    """Recursively convert numpy/pandas objects to JSON-safe Python types, replacing NaN/Inf with None."""
    # Scalars
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        x = float(obj)
        return x if math.isfinite(x) else None  # <- key line
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, pd.Period):
        return str(obj)

    # Pandas containers
    if isinstance(obj, pd.Series):
        return sanitize(obj.to_dict())
    if isinstance(obj, pd.DataFrame):
        return sanitize(obj.to_dict(orient="records"))

    # Numpy arrays
    if isinstance(obj, np.ndarray):
        return sanitize(obj.tolist())

    # Mappings / sequences
    if isinstance(obj, Mapping):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize(v) for v in obj]

    # Primitives / None
    if obj is None or isinstance(obj, (str, int)):
        return obj

    return str(obj)
def get_file_info(file_id: str) -> Optional[Dict[str, Any]]:
    """Get basic file information from the stored CSV file"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        return None
    
    # Get file stats
    stat = csv_file.stat()
    return {
        "file_id": file_id,
        "filename": csv_file.name,
        "upload_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "file_size": stat.st_size
    }

def analyze_financial_transactions(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze financial transaction data specifically"""
    # Add ML-predicted categories
    df_with_ml = categorize_transactions(df.copy())
    
    analysis = {
        "transaction_summary": {},
        "spending_analysis": {},
        "category_analysis": {},
        "time_analysis": {},
        "data_quality": {}
    }
    
    # Basic transaction summary
    analysis["transaction_summary"] = {
        "total_transactions": len(df),
        "date_range": {},
        "total_amount": 0
    }
    
    # Try to identify amount column
    amount_columns = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['amount', 'debit', 'credit', 'value']):
            amount_columns.append(col)
    
    if amount_columns:
        amount_col = amount_columns[0]  # Use first found amount column
        
        # Convert to numeric, handling common formats
        df[amount_col] = pd.to_numeric(df[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
        
        # Calculate total amount
        total_amount = df[amount_col].sum()
        analysis["transaction_summary"]["total_amount"] = float(total_amount)
        
        # Spending analysis
        positive_amounts = df[df[amount_col] > 0][amount_col]
        negative_amounts = df[df[amount_col] < 0][amount_col]
        
        analysis["spending_analysis"] = {
            "total_income": float(positive_amounts.sum()) if len(positive_amounts) > 0 else 0,
            "total_expenses": float(abs(negative_amounts.sum())) if len(negative_amounts) > 0 else 0,
            "net_amount": float(total_amount),
            "average_transaction": float(df[amount_col].mean()) if len(df) > 0 else 0,
            "largest_transaction": float(df[amount_col].max()) if len(df) > 0 else 0,
            "smallest_transaction": float(df[amount_col].min()) if len(df) > 0 else 0
        }
        
        # ML Category-based spending analysis
        if 'ml_category' in df_with_ml.columns:
            # Calculate spending by ML category
            category_spending = {}
            for category in df_with_ml['ml_category'].unique():
                category_transactions = df_with_ml[df_with_ml['ml_category'] == category]
                category_amounts = category_transactions[amount_col]
                category_spending[category] = {
                    "total_amount": float(category_amounts.sum()),
                    "transaction_count": len(category_transactions),
                    "average_amount": float(category_amounts.mean()) if len(category_transactions) > 0 else 0
                }
            
            analysis["spending_analysis"]["category_breakdown"] = category_spending
    
    # Try to identify date column
    date_columns = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['date', 'time']):
            date_columns.append(col)
    
    if date_columns:
        date_col = date_columns[0]
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            valid_dates = df[date_col].dropna()
            
            if len(valid_dates) > 0:
                analysis["transaction_summary"]["date_range"] = {
                    "start_date": valid_dates.min().isoformat(),
                    "end_date": valid_dates.max().isoformat(),
                    "days_covered": (valid_dates.max() - valid_dates.min()).days
                }
                
                # Time analysis
                analysis["time_analysis"] = {
                    "transactions_by_month": valid_dates.dt.to_period('M').astype(str).value_counts().to_dict(),
                    "transactions_by_day_of_week": valid_dates.dt.day_name().astype(str).value_counts().to_dict()
                }
                
                # Time series analysis for income and spending
                if amount_col and 'ml_category' in df_with_ml.columns:
                    # Create time series data
                    df_with_ml[date_col] = pd.to_datetime(df_with_ml[date_col], errors='coerce')
                    df_time_series = df_with_ml.dropna(subset=[date_col, amount_col]).copy()
                    
                    if len(df_time_series) > 0:
                        # Convert amount to numeric
                        df_time_series[amount_col] = pd.to_numeric(
                            df_time_series[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), 
                            errors='coerce'
                        )
                        
                        # Separate income and spending
                        income_data = df_time_series[df_time_series['ml_category'] == 'Income']
                        spending_data = df_time_series[df_time_series['ml_category'] != 'Income']
                        
                        # Create time series by different periods
                        time_series = {}
                        
                        # Daily aggregation
                        if len(df_time_series) > 0:
                            daily_income = income_data.groupby(income_data[date_col].dt.date)[amount_col].sum()
                            daily_spending = spending_data.groupby(spending_data[date_col].dt.date)[amount_col].sum()
                            
                            time_series["daily"] = {
                                "income": {str(date): float(amount) for date, amount in daily_income.items()},
                                "spending": {str(date): float(amount) for date, amount in daily_spending.items()}
                            }
                        
                        # Weekly aggregation
                        if len(df_time_series) > 7:
                            weekly_income = income_data.groupby(income_data[date_col].dt.to_period('W'))[amount_col].sum()
                            weekly_spending = spending_data.groupby(spending_data[date_col].dt.to_period('W'))[amount_col].sum()
                            
                            time_series["weekly"] = {
                                "income": {str(week): float(amount) for week, amount in weekly_income.items()},
                                "spending": {str(week): float(amount) for week, amount in weekly_spending.items()}
                            }
                        
                        # Monthly aggregation
                        if len(df_time_series) > 30:
                            monthly_income = income_data.groupby(income_data[date_col].dt.to_period('M'))[amount_col].sum()
                            monthly_spending = spending_data.groupby(spending_data[date_col].dt.to_period('M'))[amount_col].sum()
                            
                            time_series["monthly"] = {
                                "income": {str(month): float(amount) for month, amount in monthly_income.items()},
                                "spending": {str(month): float(amount) for month, amount in monthly_spending.items()}
                            }
                        
                        # Add time series to analysis
                        analysis["time_series"] = time_series
                        
                        # Calculate trends
                        if len(time_series) > 0:
                            # Use the most appropriate time period for trend analysis
                            trend_data = time_series.get("monthly", time_series.get("weekly", time_series.get("daily", {})))
                            
                            if trend_data and "income" in trend_data and "spending" in trend_data:
                                income_trend = list(trend_data["income"].values())
                                spending_trend = list(trend_data["spending"].values())
                                
                                # Simple trend calculation (slope of linear regression)
                                if len(income_trend) > 1:
                                    x = list(range(len(income_trend)))
                                    income_slope = np.polyfit(x, income_trend, 1)[0] if len(income_trend) > 1 else 0
                                else:
                                    income_slope = 0
                                    
                                if len(spending_trend) > 1:
                                    x = list(range(len(spending_trend)))
                                    spending_slope = np.polyfit(x, spending_trend, 1)[0] if len(spending_trend) > 1 else 0
                                else:
                                    spending_slope = 0
                                
                                analysis["trends"] = {
                                    "income_trend": float(income_slope),
                                    "spending_trend": float(spending_slope),
                                    "income_trend_direction": "increasing" if income_slope > 0 else "decreasing" if income_slope < 0 else "stable",
                                    "spending_trend_direction": "increasing" if spending_slope > 0 else "decreasing" if spending_slope < 0 else "stable"
                                }
        except Exception as e:
            logger.warning(f"Could not parse dates: {e}")
    
    # ML Category Analysis (only use ML-predicted categories)
    if 'ml_category' in df_with_ml.columns:
        ml_category_counts = df_with_ml['ml_category'].value_counts()
        ml_confidence_stats = df_with_ml['ml_confidence'].describe()
        
        # Separate income and spending categories for better analysis
        income_transactions = df_with_ml[df_with_ml['ml_category'] == 'Income']
        spending_transactions = df_with_ml[df_with_ml['ml_category'] != 'Income']
        
        spending_category_counts = spending_transactions['ml_category'].value_counts()
        spending_confidence_stats = spending_transactions['ml_confidence'].describe()
        
        analysis["category_analysis"] = {
            "note": "Categories: Income auto-detected, Spending predicted by ML model (k-NN)",
            "income_vs_spending": {
                "income_transactions": len(income_transactions),
                "spending_transactions": len(spending_transactions),
                "income_percentage": float(len(income_transactions) / len(df_with_ml) * 100),
                "spending_percentage": float(len(spending_transactions) / len(df_with_ml) * 100)
            },
            "top_spending_categories": spending_category_counts.head(10).to_dict(),
            "unique_categories": len(ml_category_counts),
            "category_distribution": (ml_category_counts / len(df_with_ml) * 100).round(2).to_dict(),
            "spending_confidence_stats": {
                "mean_confidence": float(spending_confidence_stats['mean']) if len(spending_transactions) > 0 else 0,
                "median_confidence": float(spending_confidence_stats['50%']) if len(spending_transactions) > 0 else 0,
                "min_confidence": float(spending_confidence_stats['min']) if len(spending_transactions) > 0 else 0,
                "max_confidence": float(spending_confidence_stats['max']) if len(spending_transactions) > 0 else 0,
                "std_confidence": float(spending_confidence_stats['std']) if len(spending_transactions) > 0 else 0
            },
            "uncategorized_count": int((spending_transactions['ml_category'] == 'Uncategorized').sum()),
            "uncategorized_percentage": float((spending_transactions['ml_category'] == 'Uncategorized').mean() * 100) if len(spending_transactions) > 0 else 0
        }
    
    # Data quality analysis
    analysis["data_quality"] = {
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "columns_with_all_nulls": df.isnull().all().sum(),
        "data_types": df.dtypes.astype(str).to_dict()
    }
    
    return analysis

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Smart Financial Coach API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "smart-financial-coach-api"}

@app.get("/files")
async def list_uploaded_files():
    """List all uploaded CSV files"""
    files = []
    for csv_file in UPLOAD_DIR.glob("*.csv"):
        try:
            file_id = csv_file.stem  # Get filename without extension
            file_info = get_file_info(file_id)
            if file_info:
                files.append(file_info)
        except Exception as e:
            logger.error(f"Error reading file {csv_file}: {e}")
    
    return {"files": files, "total_files": len(files)}

@app.get("/files/registry")
async def get_hash_registry():
    """Get the hash registry for debugging purposes"""
    registry = load_hash_registry()
    return {
        "registry": registry,
        "total_hashes": len(registry)
    }

@app.get("/ml/status")
async def get_ml_status():
    """Get the status of the ML models"""
    return {
        "category_model": {
            "loaded": ML_MODEL_LOADED,
            "path": str(ML_MODEL_PATH),
            "exists": ML_MODEL_PATH.exists()
        },
        "subscription_model": {
            "loaded": SUBSCRIPTION_MODEL_LOADED,
            "path": str(SUBSCRIPTION_MODEL_PATH),
            "exists": SUBSCRIPTION_MODEL_PATH.exists()
        }
    }

@app.post("/ml/predict-category")
async def predict_single_category(description: str, k: int = 7, threshold: float = 0.25):
    """Predict spending category for a single transaction description (for spending transactions only)"""
    if not ML_MODEL_LOADED:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    category, confidence = predict_transaction_category(description, k=k, threshold=threshold)
    
    return {
        "description": description,
        "predicted_category": category,
        "confidence": confidence,
        "note": "This prediction is for spending transactions. Income transactions are automatically categorized as 'Income'.",
        "parameters": {
            "k": k,
            "threshold": threshold
        }
    }

@app.get("/files/{file_id}/categorized")
async def get_categorized_transactions(file_id: str):
    """Get transactions with ML-predicted categories"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read and parse the CSV file
        df = pd.read_csv(csv_file)
        
        # Add ML categories
        df_with_ml = categorize_transactions(df.copy())
        
        # Convert to records for JSON response
        transactions = df_with_ml.to_dict('records')
        
        return {
            "file_id": file_id,
            "total_transactions": len(transactions),
            "transactions": sanitize(transactions)
        }
        
    except Exception as e:
        logger.error(f"Error categorizing transactions for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error categorizing transactions: {str(e)}")

@app.get("/files/{file_id}/subscriptions")
async def get_subscriptions(file_id: str, threshold: float = 0.5):
    """Get detected subscriptions from transaction data"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if not SUBSCRIPTION_MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Subscription model not loaded")
    
    try:
        # Read and parse the CSV file
        df = pd.read_csv(csv_file)
        
        # Find date and description columns
        date_col = None
        description_col = None
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time']):
                date_col = col
            if any(keyword in col.lower() for keyword in ['description', 'merchant', 'payee']):
                description_col = col
        
        if not date_col or not description_col:
            raise HTTPException(status_code=400, detail="Could not find date or description columns")
        
        # Prepare data for subscription detection
        df_sub = df[[date_col, description_col]].copy()
        df_sub.columns = ['date', 'description']
        
        # Add amount column if available
        amount_col = None
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['amount', 'debit', 'credit', 'value']):
                amount_col = col
                break
        
        if amount_col:
            df_sub['amount'] = pd.to_numeric(df[amount_col], errors='coerce')
        else:
            df_sub['amount'] = 0.0
        
        # Filter to only include expenses (negative amounts or zero)
        # Income (positive amounts) should not be considered for subscription detection
        df_sub = df_sub[df_sub['amount'] <= 0].copy()
        
        if len(df_sub) == 0:
            raise HTTPException(status_code=400, detail="No expense transactions found for subscription analysis")
        
        # Detect subscriptions
        subscriptions = predict_subscriptions(df_sub, SUBSCRIPTION_MODEL, SUBSCRIPTION_FEATURE_COLS)
        
        # Filter by threshold and convert to list
        high_confidence_subscriptions = subscriptions[subscriptions['score'] >= threshold]
        
        subscription_list = []
        for _, row in high_confidence_subscriptions.iterrows():
            # Calculate average monthly cost
            # If we have coverage months, use that; otherwise estimate from median gap
            if row['coverage_months'] > 0:
                avg_monthly_cost = abs(float(row['amount_mean'])) * (row['n_occurrences'] / row['coverage_months'])
            else:
                # Estimate based on median gap (assume monthly if gap is around 30 days)
                if row['median_gap_days'] > 0:
                    estimated_frequency_per_month = 30.0 / row['median_gap_days']
                    avg_monthly_cost = abs(float(row['amount_mean'])) * estimated_frequency_per_month
                else:
                    avg_monthly_cost = abs(float(row['amount_mean']))
            
            # Find the website for this merchant
            website = find_subscription_website(row['merchant'])
            
            subscription_list.append({
                "merchant": row['merchant'],
                "subscription_score": float(row['score']),
                "occurrences": int(row['n_occurrences']),
                "coverage_months": int(row['coverage_months']),
                "median_gap_days": float(row['median_gap_days']),
                "day_consistency": float(row['dom_consistency']),
                "average_amount": float(row['amount_mean']),
                "average_monthly_cost": round(avg_monthly_cost, 2),
                "autocorrelation_30d": float(row['autocorr_30d']),
                "website": website
            })
        
        # Calculate total monthly cost
        total_monthly_cost = sum(sub['average_monthly_cost'] for sub in subscription_list)
        
        return {
            "file_id": file_id,
            "threshold": threshold,
            "total_subscriptions": len(subscription_list),
            "total_monthly_cost": round(total_monthly_cost, 2),
            "expense_transactions_analyzed": len(df_sub),
            "subscriptions": subscription_list
        }
        
    except Exception as e:
        logger.error(f"Error detecting subscriptions for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error detecting subscriptions: {str(e)}")

@app.get("/subscriptions/status")
async def get_subscription_model_status():
    """Get the status of the subscription detection model"""
    return {
        "model_loaded": SUBSCRIPTION_MODEL_LOADED,
        "model_path": str(SUBSCRIPTION_MODEL_PATH),
        "model_exists": SUBSCRIPTION_MODEL_PATH.exists(),
        "feature_columns": SUBSCRIPTION_FEATURE_COLS
    }

@app.get("/files/{file_id}/insights")
async def get_ai_insights(file_id: str):
    """Get AI-powered financial insights for the past month (30 days)"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read and parse the CSV file
        df = pd.read_csv(csv_file)
        
        # Add ML categories
        df_with_ml = categorize_transactions(df.copy())
        
        # Find amount and date columns
        amount_col = None
        date_col = None
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['amount', 'debit', 'credit', 'value']):
                amount_col = col
            if any(keyword in col.lower() for keyword in ['date', 'time']):
                date_col = col
        
        if not amount_col or not date_col:
            raise HTTPException(status_code=400, detail="Could not find amount or date columns")
        
        # Process data for the specified period
        df_with_ml[date_col] = pd.to_datetime(df_with_ml[date_col], errors='coerce')
        df_time_series = df_with_ml.dropna(subset=[date_col, amount_col]).copy()
        
        if len(df_time_series) == 0:
            raise HTTPException(status_code=400, detail="No valid time series data found")
        
        # Convert amount to numeric
        df_time_series[amount_col] = pd.to_numeric(
            df_time_series[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        )
        
        # Filter data for the past month (30 days)
        end_date = df_time_series[date_col].max()
        start_date = end_date - pd.Timedelta(days=29)  # 30 days inclusive
        
        # Filter data to the past month
        df_current = df_time_series[df_time_series[date_col] >= start_date].copy()
        
        # Get prior period for comparison
        prior_start = start_date - (end_date - start_date)
        df_prior = df_time_series[
            (df_time_series[date_col] >= prior_start) & 
            (df_time_series[date_col] < start_date)
        ].copy()
        
        if len(df_current) == 0:
            raise HTTPException(status_code=400, detail="No data found for the past month (30 days)")
        
        # Separate income and spending
        income_current = df_current[df_current['ml_category'] == 'Income']
        spending_current = df_current[df_current['ml_category'] != 'Income']
        
        income_prior = df_prior[df_prior['ml_category'] == 'Income']
        spending_prior = df_prior[df_prior['ml_category'] != 'Income']
        
        # Calculate current period metrics
        current_income = float(income_current[amount_col].sum())
        current_expenses = float(abs(spending_current[amount_col].sum()))
        current_net = current_income - current_expenses
        
        # Calculate prior period metrics
        prior_income = float(income_prior[amount_col].sum())
        prior_expenses = float(abs(spending_prior[amount_col].sum()))
        prior_net = prior_income - prior_expenses
        
        # Calculate category deltas
        current_categories = spending_current.groupby('ml_category')[amount_col].sum().abs()
        prior_categories = spending_prior.groupby('ml_category')[amount_col].sum().abs()
        
        category_deltas = []
        for category in current_categories.index:
            current_amount = float(current_categories[category])
            prior_amount = float(prior_categories.get(category, 0))
            delta = current_amount - prior_amount
            category_deltas.append({
                "category": category,
                "current_amount": current_amount,
                "prior_amount": prior_amount,
                "delta_amount": delta
            })
        
        # Get top merchants
        top_merchants = []
        if 'description' in df_current.columns:
            merchant_counts = df_current[df_current['ml_category'] != 'Income']['description'].value_counts().head(5)
            for merchant, count in merchant_counts.items():
                merchant_amount = float(df_current[df_current['description'] == merchant][amount_col].sum())
                top_merchants.append({
                    "merchant": merchant,
                    "count": int(count),
                    "total_amount": abs(merchant_amount)
                })
        
        # Get subscription data
        subscriptions = []
        if SUBSCRIPTION_MODEL_LOADED:
            try:
                df_sub = df_current[[date_col, 'description']].copy()
                df_sub.columns = ['date', 'description']
                df_sub['amount'] = pd.to_numeric(df_current[amount_col], errors='coerce')
                df_sub = df_sub[df_sub['amount'] <= 0].copy()
                
                if len(df_sub) > 0:
                    subs_data = predict_subscriptions(df_sub, SUBSCRIPTION_MODEL, SUBSCRIPTION_FEATURE_COLS)
                    high_confidence_subs = subs_data[subs_data['score'] >= 0.5]
                    
                    for _, row in high_confidence_subs.iterrows():
                        subscriptions.append({
                            "merchant": row['merchant'],
                            "score": float(row['score']),
                            "amount_mean": float(row['amount_mean']),
                            "n_occurrences": int(row['n_occurrences'])
                        })
            except Exception as e:
                logger.warning(f"Could not get subscription data: {e}")
        
        # Prepare inputs for LLM
        llm_inputs = {
            "time_range": "Last 30d",
            "income": current_income,
            "expenses": current_expenses,
            "net": current_net,
            "prior_net": prior_net,
            "category_deltas": category_deltas,
            "top_merchants": top_merchants,
            "subscriptions": subscriptions,
            "cash_balance": None  # Could be added if available
        }
        
        # Generate AI insights
        try:
            insights = generate_llm_cards(llm_inputs)
            return {
                "file_id": file_id,
                "period": "30d",
                "insights": insights,
                "summary": {
                    "current_income": current_income,
                    "current_expenses": current_expenses,
                    "current_net": current_net,
                    "prior_net": prior_net,
                    "net_change": current_net - prior_net
                }
            }
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating AI insights: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error generating insights for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.get("/files/{file_id}/time-series")
async def get_time_series_data(file_id: str, period: str = "30d"):
    """Get cumulative time series data for income and spending trends"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if period not in ["14d", "30d", "90d", "1y"]:
        raise HTTPException(status_code=400, detail="Period must be '14d', '30d', '90d', or '1yr'")
    
    try:
        # Read and parse the CSV file
        df = pd.read_csv(csv_file)
        
        # Add ML categories
        df_with_ml = categorize_transactions(df.copy())
        
        # Find amount and date columns
        amount_col = None
        date_col = None
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['amount', 'debit', 'credit', 'value']):
                amount_col = col
            if any(keyword in col.lower() for keyword in ['date', 'time']):
                date_col = col
        
        if not amount_col or not date_col:
            raise HTTPException(status_code=400, detail="Could not find amount or date columns")
        
        # Process time series data
        df_with_ml[date_col] = pd.to_datetime(df_with_ml[date_col], errors='coerce')
        df_time_series = df_with_ml.dropna(subset=[date_col, amount_col]).copy()
        
        if len(df_time_series) == 0:
            raise HTTPException(status_code=400, detail="No valid time series data found")
        
        # Convert amount to numeric
        df_time_series[amount_col] = pd.to_numeric(
            df_time_series[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        )
        
        # Filter data based on time period
        end_date = df_time_series[date_col].max()
        
        if period == "14d":
            start_date = end_date - pd.Timedelta(days=14)
        elif period == "30d":
            start_date = end_date - pd.Timedelta(days=30)
        elif period == "90d":
            start_date = end_date - pd.Timedelta(days=90)
        else:  # 1y
            start_date = end_date - pd.Timedelta(days=365)
        
        # Filter data to the specified time period
        df_filtered = df_time_series[df_time_series[date_col] >= start_date].copy()
        
        if len(df_filtered) == 0:
            raise HTTPException(status_code=400, detail=f"No data found for the specified period: {period}")
        
        # Sort by date
        df_filtered = df_filtered.sort_values(date_col)
        
        # Separate income and spending
        income_data = df_filtered[df_filtered['ml_category'] == 'Income']
        spending_data = df_filtered[df_filtered['ml_category'] != 'Income']
        
        # Create daily aggregation
        daily_income = income_data.groupby(income_data[date_col].dt.date)[amount_col].sum()
        daily_spending = spending_data.groupby(spending_data[date_col].dt.date)[amount_col].sum()
        
        # Create a complete date range for the period
        date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
        
        # Initialize cumulative totals
        cumulative_income = 0.0
        cumulative_spending = 0.0
        
        # Build cumulative time series
        income_series = []
        spending_series = []
        
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            
            # Add daily amounts to cumulative totals
            if date.date() in daily_income.index:
                cumulative_income += float(daily_income[date.date()])
            if date.date() in daily_spending.index:
                cumulative_spending += float(daily_spending[date.date()])
            
            income_series.append({
                "date": date_str,
                "cumulative_amount": cumulative_income,
                "daily_amount": float(daily_income.get(date.date(), 0))
            })
            
            spending_series.append({
                "date": date_str,
                "cumulative_amount": abs(cumulative_spending),  # Make spending positive for visualization
                "daily_amount": abs(float(daily_spending.get(date.date(), 0)))
            })
        
        # Calculate summary statistics
        total_income = float(income_data[amount_col].sum())
        total_spending = float(spending_data[amount_col].sum())
        
        time_series_data = {
            "period": period,
            "date_range": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "days_covered": len(date_range)
            },
            "income": income_series,
            "spending": spending_series,
            "summary": {
                "total_income": total_income,
                "total_spending": abs(total_spending),
                "net_amount": total_income - abs(total_spending),
                "data_points": len(income_series),
                "income_transactions": len(income_data),
                "spending_transactions": len(spending_data)
            }
        }
        
        return time_series_data
        
    except Exception as e:
        logger.error(f"Error generating time series for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating time series: {str(e)}")

@app.get("/files/{file_id}/categories-by-time")
async def get_categories_by_time(file_id: str, period: str = "30d"):
    """Get spending categories analysis by time period"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if period not in ["14d", "30d", "90d", "1y"]:
        raise HTTPException(status_code=400, detail="Period must be '14d', '30d', '90d', or '1y'")
    
    try:
        # Read and parse the CSV file
        df = pd.read_csv(csv_file)
        
        # Add ML categories
        df_with_ml = categorize_transactions(df.copy())
        
        # Find amount and date columns
        amount_col = None
        date_col = None
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['amount', 'debit', 'credit', 'value']):
                amount_col = col
            if any(keyword in col.lower() for keyword in ['date', 'time']):
                date_col = col
        
        if not amount_col or not date_col:
            raise HTTPException(status_code=400, detail="Could not find amount or date columns")
        
        # Process time series data
        df_with_ml[date_col] = pd.to_datetime(df_with_ml[date_col], errors='coerce')
        df_time_series = df_with_ml.dropna(subset=[date_col, amount_col]).copy()
        
        if len(df_time_series) == 0:
            raise HTTPException(status_code=400, detail="No valid time series data found")
        
        # Convert amount to numeric
        df_time_series[amount_col] = pd.to_numeric(
            df_time_series[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        )
        
        # Filter data based on time period
        end_date = df_time_series[date_col].max()
        
        if period == "14d":
            start_date = end_date - pd.Timedelta(days=13)
        elif period == "30d":
            start_date = end_date - pd.Timedelta(days=29)
        elif period == "90d":
            start_date = end_date - pd.Timedelta(days=89)
        else:  # 1y
            start_date = end_date - pd.Timedelta(days=364)
        
        # Filter data to the specified time period
        df_filtered = df_time_series[df_time_series[date_col] >= start_date].copy()
        
        if len(df_filtered) == 0:
            raise HTTPException(status_code=400, detail=f"No data found for the specified period: {period}")
        
        # Separate income and spending
        income_data = df_filtered[df_filtered['ml_category'] == 'Income']
        spending_data = df_filtered[df_filtered['ml_category'] != 'Income']
        
        # Analyze spending categories
        category_analysis = {}
        
        if len(spending_data) > 0:
            # Group by category and calculate statistics
            category_groups = spending_data.groupby('ml_category')
            
            for category, group in category_groups:
                category_amounts = group[amount_col]
                category_analysis[category] = {
                    "total_amount": float(abs(category_amounts.sum())),
                    "transaction_count": len(group),
                    "average_amount": float(abs(category_amounts.mean())),
                    "min_amount": float(abs(category_amounts.min())),
                    "max_amount": float(abs(category_amounts.max())),
                    "percentage_of_spending": float(abs(category_amounts.sum()) / abs(spending_data[amount_col].sum()) * 100)
                }
        
        # Sort categories by total amount
        sorted_categories = sorted(category_analysis.items(), key=lambda x: x[1]['total_amount'], reverse=True)
        
        # Calculate summary statistics
        total_income = float(income_data[amount_col].sum())
        total_spending = float(spending_data[amount_col].sum())
        
        categories_data = {
            "period": period,
            "date_range": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "days_covered": (end_date - start_date).days + 1
            },
            "summary": {
                "total_income": total_income,
                "total_spending": abs(total_spending),
                "net_amount": total_income - abs(total_spending),
                "income_transactions": len(income_data),
                "spending_transactions": len(spending_data),
                "unique_categories": len(category_analysis)
            },
            "top_categories": dict(sorted_categories[:10]),  # Top 10 categories
            "all_categories": dict(sorted_categories)
        }
        
        return categories_data
        
    except Exception as e:
        logger.error(f"Error generating categories by time for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating categories by time: {str(e)}")

@app.get("/files/{file_id}")
async def get_file_details(file_id: str):
    """Get basic information about a specific uploaded file"""
    file_info = get_file_info(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_info

@app.get("/files/{file_id}/analysis")
async def get_file_analysis(file_id: str):
    """Generate and return financial analysis for a specific file"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read and parse the CSV file
        df = pd.read_csv(csv_file)
        df = df.copy()
        
        # Generate analysis
        analysis = analyze_financial_transactions(df)
        
        # Add basic file info
        analysis["file_info"] = {
            "file_id": file_id,
            "filename": csv_file.name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "sample_data": df.head(5).to_dict('records')
        }
        
        return sanitize(analysis)
        
    except Exception as e:
        logger.exception(f"Error analyzing file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")

@app.post("/upload-transactions")
async def upload_transaction_csv(file: UploadFile = File(...)):
    """
    Upload a financial transaction CSV file
    
    Args:
        file: CSV file containing transaction data
        
    Returns:
        JSON response with file ID for future reference
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400, 
                detail="File must be a CSV file"
            )
        
        # Read file content
        content = await file.read()
        
        # Calculate file hash to check for duplicates
        file_hash = calculate_file_hash(content)
        
        # Check if this file already exists
        existing_file = find_duplicate_file(file_hash)
        if existing_file:
            logger.info(f"Duplicate file detected: {file.filename} (same as {existing_file['filename']})")
            return JSONResponse(
                status_code=200,
                content={
                    "message": "File already exists (duplicate detected)",
                    "file_id": existing_file["file_id"],
                    "filename": existing_file["filename"],
                    "original_upload_time": existing_file["upload_time"],
                    "is_duplicate": True
                }
            )
        
        # Generate unique file ID for new file
        file_id = str(uuid.uuid4())
        
        # Save the original file
        csv_file_path = UPLOAD_DIR / f"{file_id}.csv"
        with open(csv_file_path, 'w', encoding='utf-8') as f:
            f.write(content.decode('utf-8'))
        
        # Register the file hash
        register_file_hash(file_hash, file_id, file.filename)
        
        # Basic validation - try to parse the CSV
        try:
            csv_data = io.StringIO(content.decode('utf-8'))
            df = pd.read_csv(csv_data)
            
            logger.info(f"Successfully uploaded financial CSV: {file.filename} with {len(df)} transactions")
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Financial transaction CSV uploaded successfully",
                    "file_id": file_id,
                    "filename": file.filename,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "is_duplicate": False
                }
            )
            
        except pd.errors.EmptyDataError:
            # Clean up saved file and hash registration
            csv_file_path.unlink(missing_ok=True)
            # Remove from hash registry
            registry = load_hash_registry()
            registry.pop(file_hash, None)
            save_hash_registry(registry)
            raise HTTPException(
                status_code=400,
                detail="The CSV file is empty"
            )
        except pd.errors.ParserError as e:
            # Clean up saved file and hash registration
            csv_file_path.unlink(missing_ok=True)
            # Remove from hash registry
            registry = load_hash_registry()
            registry.pop(file_hash, None)
            save_hash_registry(registry)
            raise HTTPException(
                status_code=400,
                detail=f"Error parsing CSV file: {str(e)}"
            )
        except UnicodeDecodeError:
            # Clean up saved file and hash registration
            csv_file_path.unlink(missing_ok=True)
            # Remove from hash registry
            registry = load_hash_registry()
            registry.pop(file_hash, None)
            save_hash_registry(registry)
            raise HTTPException(
                status_code=400,
                detail="File encoding error. Please ensure the file is UTF-8 encoded"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded CSV file and clean up hash registry"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Remove from hash registry
    registry = load_hash_registry()
    # Find and remove the hash entry for this file_id
    hash_to_remove = None
    for file_hash, file_info in registry.items():
        if file_info["file_id"] == file_id:
            hash_to_remove = file_hash
            break
    
    if hash_to_remove:
        registry.pop(hash_to_remove, None)
        save_hash_registry(registry)
    
    # Delete the actual file
    csv_file.unlink()
    return {"message": f"File {file_id} deleted successfully"}

@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """Download the original CSV file"""
    csv_file = UPLOAD_DIR / f"{file_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=csv_file,
        filename=csv_file.name,
        media_type="text/csv"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)