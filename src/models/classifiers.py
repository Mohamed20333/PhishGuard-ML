"""
Model Definitions — PhishGuard Classifier Suite
================================================
Implements five individual classifiers plus a Voting Ensemble.
All models follow the sklearn API for interoperability.

References
----------
- Logistic Regression  : baseline linear model
- Decision Tree        : interpretable tree-based model
- Random Forest        : bagging ensemble, high recall
- XGBoost              : gradient boosting, best individual model
- MLP Neural Network   : deep learning for non-linear patterns
- Voting Ensemble      : RF + XGB + MLP soft-voting meta-classifier
"""

import os
import joblib
import logging
import numpy as np
from sklearn.linear_model    import LogisticRegression
from sklearn.tree            import DecisionTreeClassifier
from sklearn.ensemble        import RandomForestClassifier, VotingClassifier
from sklearn.neural_network  import MLPClassifier
from xgboost                 import XGBClassifier

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.config import (LR_PARAMS, DT_PARAMS, RF_PARAMS, XGB_PARAMS,
                            MLP_PARAMS, MODELS_DIR, RANDOM_STATE)

logger = logging.getLogger(__name__)


def build_models() -> dict:
    """
    Instantiate all five classifiers and the ensemble.

    Returns
    -------
    dict : model_name → sklearn estimator
    """
    lr  = LogisticRegression(**LR_PARAMS)
    dt  = DecisionTreeClassifier(**DT_PARAMS)
    rf  = RandomForestClassifier(**RF_PARAMS)
    xgb = XGBClassifier(**XGB_PARAMS, verbosity=0)
    mlp = MLPClassifier(**MLP_PARAMS)

    # Soft-voting ensemble: combines probability estimates
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("xgb", xgb), ("mlp", mlp)],
        voting="soft",
        n_jobs=-1,
    )

    return {
        "Logistic Regression" : lr,
        "Decision Tree"       : dt,
        "Random Forest"       : rf,
        "XGBoost"             : xgb,
        "MLP Neural Network"  : mlp,
        "PhishGuard Ensemble" : ensemble,
    }


def save_model(model, name: str) -> str:
    """Serialize a trained model to disk via joblib."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    safe_name = name.replace(" ", "_").lower()
    path = os.path.join(MODELS_DIR, f"{safe_name}.joblib")
    joblib.dump(model, path)
    logger.info(f"Saved model → {path}")
    return path


def load_model(name: str):
    """Load a serialized model by its display name."""
    safe_name = name.replace(" ", "_").lower()
    path = os.path.join(MODELS_DIR, f"{safe_name}.joblib")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}")
    return joblib.load(path)
