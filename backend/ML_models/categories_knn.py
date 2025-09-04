# backend/app/model_knn.py
import re
import numpy as np
import joblib
from pathlib import Path
from typing import Tuple

MODEL_PATH = Path(__file__).parent / "knn_model.joblib"

_pack = None
_vec = None
_nn = None
_y = None


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


def load_model():
    global _pack, _vec, _nn, _y
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. "
            f"Train it first with: python backend/train/train_knn.py"
        )
    _pack = joblib.load(MODEL_PATH)
    _vec = _pack["vectorizer"]
    _nn = _pack["nn"]
    _y = _pack["y"]

def normalize_category(category: str) -> str:
    """
    Normalize category names to treat 'Other' and 'Uncategorized' as the same.
    """
    if category in ["Other", "Uncategorized"]:
        return "Uncategorized"
    return category

def knn_predict(desc: str, k: int = 3, threshold: float = 0.35) -> Tuple[str, float]:
    """
    Returns (label, confidence). Cosine distance -> similarity = 1 - dist.
    Confidence = avg similarity of neighbors belonging to the winning class.
    Treats 'Other' and 'Uncategorized' as the same category.
    """
    if _vec is None or _nn is None or _y is None:
        load_model()

    x = _vec.transform([normalize(desc)])
    dists, idxs = _nn.kneighbors(x, n_neighbors=k, return_distance=True)
    dists, idxs = dists[0], idxs[0]
    sims = 1.0 - dists  # cosine similarity in [0..1]
    labels = _y[idxs]

    # Normalize categories to treat 'Other' and 'Uncategorized' as the same
    normalized_labels = [normalize_category(label) for label in labels]

    # Majority vote; tie-break by sum(similarities)
    buckets = {}
    for lab, sim in zip(normalized_labels, sims):
        buckets.setdefault(lab, []).append(sim)

    best_label = None
    best_key = (-1, -1.0)
    for lab, arr in buckets.items():
        key = (len(arr), float(np.sum(arr)))
        if key > best_key:
            best_key = key
            best_label = lab

    confidence = float(np.mean(buckets[best_label]))
    if confidence < threshold:
        return "Uncategorized", confidence
    return best_label, confidence
