# backend/train/train_knn.py
import pandas as pd, re, joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "training_data" / "category_training_data.csv"
MODEL_PATH = ROOT / "ML_models" / "knn_model.joblib"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

CITY_STATES = r"( AL| AK| AZ| AR| CA| CO| CT| DC| DE| FL| GA| HI| IA| ID| IL| IN| KS| KY| LA| MA| MD| ME| MI| MN| MO| MS| MT| NC| ND| NE| NH| NJ| NM| NV| NY| OH| OK| OR| PA| RI| SC| SD| TN| TX| UT| VA| VT| WA| WI| WV)\b"

def normalize(t: str) -> str:
    t = str(t).upper()
    t = re.sub(r"\s+", " ", t)
    # remove POS/terminal/codes/dates
    t = re.sub(r"\b(POS|DBT|CRD|CHK|TRN|ATM|XFER|WITHDRAWAL|DEPOSIT)\b", " ", t)
    t = re.sub(r"\b#?\d{3,}\b", " ", t)                 # store/order numbers
    t = re.sub(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", " ", t) # dates
    t = re.sub(CITY_STATES, " ", t)                     # trailing state
    t = re.sub(r"\b(USA|US|UNITED STATES)\b", " ", t)
    t = re.sub(r"[^A-Z&' ]", " ", t)                    # drop punctuation except & and '
    t = re.sub(r"\s+", " ", t).strip()
    return t

def normalize_category(category: str) -> str:
    """
    Normalize category names to treat 'Other' and 'Uncategorized' as the same.
    """
    if category in ["Other", "Uncategorized"]:
        return "Uncategorized"
    return category

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing labeled data: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    if not {"description", "category"}.issubset(df.columns):
        raise ValueError("CSV must have columns: description, category")

    df = df.dropna(subset=["description", "category"]).copy()
    df["description_norm"] = df["description"].map(normalize)
    
    # Normalize categories to treat 'Other' and 'Uncategorized' as the same
    df["category_norm"] = df["category"].astype(str).map(normalize_category)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        max_features=30000,
    )
    X = vectorizer.fit_transform(df["description_norm"].values)
    y = df["category_norm"].values

    # k-NN on cosine distance
    nn = NearestNeighbors(metric="cosine", n_neighbors=5)
    nn.fit(X)

    joblib.dump({"vectorizer": vectorizer, "nn": nn, "y": y}, MODEL_PATH)
    print(f"✅ Saved model to {MODEL_PATH}")
    print(f"📊 Categories in model: {sorted(set(y))}")
    print(f"📈 Total training samples: {len(y)}")

if __name__ == "__main__":
    main()
