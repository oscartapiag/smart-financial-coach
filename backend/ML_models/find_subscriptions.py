import pandas as pd, numpy as np, re, json, joblib
from datetime import timedelta
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.impute import SimpleImputer


# Seed labels from your generator
SUBS_MERCHANTS = {"NETFLIX","SPOTIFY","ICLOUD","CITY GYM"}

def _norm_merchant(s: pd.Series) -> pd.Series:
    return (s.astype(str).str.upper()
            .str.replace(r"[^A-Z0-9&+ ]", "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip())

def _autocorr_at_lag(binary_daily: pd.Series, lag_days: int = 30) -> float:
    x = binary_daily.values.astype(float)
    if len(x) <= lag_days: return 0.0
    x0, x1 = x[:-lag_days], x[lag_days:]
    if x0.std() == 0 or x1.std() == 0: return 0.0
    return float(np.corrcoef(x0, x1)[0,1])

def merchant_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x = x.dropna(subset=["date","description"])
    x["amount"] = pd.to_numeric(x.get("amount", np.nan), errors="coerce")
    x["_m"] = _norm_merchant(x["description"])

    feats = []
    for m, g in x.groupby("_m"):
        g = g.sort_values("date")
        n = len(g)

        # gaps
        if n >= 2:
            gaps = g["date"].diff().dropna().dt.days
            if not gaps.empty and gaps.mean() and np.isfinite(gaps.mean()):
                gap_cv = float(gaps.std() / gaps.mean())
            else:
                gap_cv = 1.0
            median_gap = float(np.median(gaps)) if not gaps.empty else 0.0
            span_days = int((g["date"].max() - g["date"].min()).days)
        else:
            gap_cv = 1.0
            median_gap = 0.0
            span_days = 0

        # amount stability
        amt = g["amount"].dropna()
        amt_mean = float(amt.mean()) if len(amt) else 0.0
        if len(amt) > 1 and abs(amt_mean) > 1e-9:
            amt_cv = float(amt.std() / abs(amt_mean))
        else:
            amt_cv = 0.0
        if len(amt) >= 4 and abs(amt_mean) > 1e-9:
            q1, q3 = np.percentile(amt, [25, 75]); iqr = q3 - q1
            amt_iqr_ratio = float(iqr / abs(amt_mean)) if np.isfinite(iqr) else 0.0
        else:
            amt_iqr_ratio = 0.0

        months = g["date"].dt.to_period("M").astype(str).nunique()
        dom = g["date"].dt.day
        dom_mode = int(dom.mode().iat[0]) if len(dom) else 0
        dom_consistency = float((dom == dom_mode).mean()) if len(dom) else 0.0

        # daily autocorr
        daily = (g.set_index(g["date"].dt.floor("D"))
                   .assign(hit=1)["hit"]
                   .resample("D").max().fillna(0))
        ac30 = _autocorr_at_lag(daily, 30)

        share_negative = float((g["amount"] < 0).mean()) if "amount" in g else 1.0

        feats.append({
            "merchant": m,
            "n_occurrences": int(n),
            "coverage_months": int(months),
            "median_gap_days": float(median_gap),
            "gap_cv": float(gap_cv),
            "day_of_month_mode": dom_mode,
            "dom_consistency": float(dom_consistency),
            "amount_mean": float(amt_mean),
            "amount_cv": float(amt_cv),
            "amount_iqr_ratio": float(amt_iqr_ratio),
            "autocorr_30d": float(ac30) if np.isfinite(ac30) else 0.0,
            "share_negative": float(share_negative),
            "span_days": int(span_days),
        })

    F = pd.DataFrame(feats)
    if F.empty:
        return F
    # ensure numeric cols are finite
    num_cols = [c for c in F.columns if c != "merchant"]
    F[num_cols] = F[num_cols].replace([np.inf, -np.inf], np.nan)
    return F


def label_from_known(feats: pd.DataFrame) -> pd.Series:
    return feats["merchant"].apply(lambda m: 1 if any(s in m for s in SUBS_MERCHANTS) else 0)

def train_subscription_model(df_train: pd.DataFrame):
    feats = merchant_features(df_train)
    y = label_from_known(feats)
    X = feats.drop(columns=["merchant"])

    # Guard: need both classes to train logreg
    if y.nunique() < 2:
        raise ValueError("Training data has only one class; add at least one positive and one negative merchant.")

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value=0.0)),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=200, class_weight="balanced"))
    ])

    Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    model.fit(Xtr, ytr)
    p = model.predict_proba(Xva)[:, 1]
    print("AUC:", roc_auc_score(yva, p))
    print(classification_report(yva, (p >= 0.5).astype(int)))
    return model, list(X.columns)

def predict_subscriptions(df_any: pd.DataFrame, model, feature_cols):
    feats = merchant_features(df_any)
    X = feats.drop(columns=["merchant"])
    # align columns
    for c in feature_cols:
        if c not in X.columns: X[c] = 0.0
    X = X[feature_cols]
    scores = model.predict_proba(X)[:,1]
    out = feats[["merchant"]].copy()
    out["score"] = scores
    out["n_occurrences"] = feats["n_occurrences"]
    out["coverage_months"] = feats["coverage_months"]
    out["median_gap_days"] = feats["median_gap_days"]
    out["dom_consistency"] = feats["dom_consistency"]
    out["amount_mean"] = feats["amount_mean"]
    out["autocorr_30d"] = feats["autocorr_30d"]
    return out.sort_values("score", ascending=False)

def save_model(model, feature_cols, model_path: str, cols_path: str):
    joblib.dump(model, model_path)
    with open(cols_path, "w") as f: json.dump(feature_cols, f)

def load_model(model_path: str, cols_path: str):
    model = joblib.load(model_path)
    with open(cols_path) as f: cols = json.load(f)
    return model, cols
