# train_subscriptions.py
import pandas as pd
from pathlib import Path
from find_subscriptions import train_subscription_model, save_model

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATA = BASE_DIR / "trans_data_internal" / "sample_transactions_balanced.csv"

MODELS_DIR = Path("ML_models"); MODELS_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODELS_DIR / "subscriptions_v1.joblib"
COLS_PATH  = MODELS_DIR / "subscriptions_v1.cols.json"

def main():
    df = pd.read_csv(DATA)
    model, cols = train_subscription_model(df)
    save_model(model, cols, str(MODEL_PATH), str(COLS_PATH))
    print(f"✅ Saved model → {MODEL_PATH}")
    print(f"✅ Saved feature cols → {COLS_PATH}")

if __name__ == "__main__":
    main()
