"""
PhishGuard Configuration
========================
Central configuration for the phishing URL detection pipeline.
"""

import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
RAW_DIR     = os.path.join(DATA_DIR, "raw")
PROCESSED   = os.path.join(DATA_DIR, "processed")
ARTIFACTS   = os.path.join(BASE_DIR, "artifacts")
MODELS_DIR  = os.path.join(ARTIFACTS, "models")
PLOTS_DIR   = os.path.join(ARTIFACTS, "plots")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# ── Dataset ────────────────────────────────────────────────────────────────────
DATASET_URL  = "https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning"
RANDOM_STATE = 42
TEST_SIZE    = 0.15          # 70 / 15 / 15 split
VAL_SIZE     = 0.15
TARGET_COL   = "label"       # 1 = phishing, 0 = legitimate

# ── Feature Engineering ────────────────────────────────────────────────────────
SUSPICIOUS_WORDS = [
    "login", "secure", "account", "update", "verify", "banking",
    "confirm", "password", "paypal", "signin", "webscr", "ebay",
    "support", "wallet", "alert", "billing", "authentication",
]
URL_SHORTENERS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "adf.ly", "short.to", "bc.vc",
]

# ── Model Hyperparameters ──────────────────────────────────────────────────────
LR_PARAMS  = {"C": 1.0, "max_iter": 1000, "solver": "lbfgs", "random_state": RANDOM_STATE}
DT_PARAMS  = {"max_depth": 10, "min_samples_split": 5, "random_state": RANDOM_STATE}
RF_PARAMS  = {"n_estimators": 200, "max_depth": 15, "min_samples_split": 4,
               "n_jobs": -1, "random_state": RANDOM_STATE}
XGB_PARAMS = {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.1,
               "subsample": 0.8, "colsample_bytree": 0.8,
               "use_label_encoder": False, "eval_metric": "logloss",
               "random_state": RANDOM_STATE}
MLP_PARAMS = {"hidden_layer_sizes": (128, 64, 32), "activation": "relu",
               "solver": "adam", "alpha": 0.001, "learning_rate": "adaptive",
               "max_iter": 300, "random_state": RANDOM_STATE}

# ── Evaluation ─────────────────────────────────────────────────────────────────
CV_FOLDS    = 5
METRIC_MAIN = "f1"           # primary metric for model selection

# ── Visualization ──────────────────────────────────────────────────────────────
PALETTE = {
    "dark_bg"    : "#0D1117",
    "panel"      : "#161B22",
    "accent_blue": "#58A6FF",
    "accent_green": "#3FB950",
    "accent_red" : "#F85149",
    "accent_gold": "#D29922",
    "text"       : "#C9D1D9",
    "grid"       : "#21262D",
}
FIGSIZE_SINGLE = (8, 5)
FIGSIZE_WIDE   = (14, 5)
DPI            = 150
