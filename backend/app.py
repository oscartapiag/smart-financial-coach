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
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import pandas as pd
from collections.abc import Mapping, Sequence



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Financial Coach API",
    description="API for processing financial transaction CSV files",
    version="1.0.0"
)

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

def sanitize(obj):
    """Recursively convert numpy/pandas objects to JSON-safe Python types."""
    # Scalars
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    if isinstance(obj, (pd.Period,)):
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

    # Primitives or None
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Fallback
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
        except Exception as e:
            logger.warning(f"Could not parse dates: {e}")
    
    # Try to identify category column
    category_columns = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['category', 'type', 'description', 'merchant']):
            category_columns.append(col)
    
    if category_columns:
        category_col = category_columns[0]
        category_counts = df[category_col].value_counts()
        analysis["category_analysis"] = {
            "top_categories": category_counts.head(10).to_dict(),
            "unique_categories": len(category_counts),
            "category_distribution": (category_counts / len(df) * 100).round(2).to_dict()
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