"""
Training Module — PhishGuard
=============================
Trains all classifiers, performs cross-validation, and logs results.
"""

import logging
import time
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics         import f1_score
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.config          import CV_FOLDS, METRIC_MAIN, RANDOM_STATE
from src.models.classifiers import build_models, save_model

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trains each model, records training time and CV results.

    Attributes
    ----------
    results_   : dict  — per-model training summary
    models_    : dict  — fitted estimators
    """

    def __init__(self):
        self.results_ = {}
        self.models_  = {}

    def train_all(self, X_train: np.ndarray, y_train: np.ndarray,
                  X_val: np.ndarray, y_val: np.ndarray) -> dict:
        """
        Train every model and evaluate on validation set.

        Returns
        -------
        dict : model_name → {val_f1, val_acc, train_time, cv_mean, cv_std}
        """
        models = build_models()
        cv     = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True,
                                 random_state=RANDOM_STATE)

        for name, model in models.items():
            logger.info(f"Training: {name} ...")
            t0 = time.perf_counter()

            # ── Cross-validation on training data ─────────────────────────────
            cv_scores = cross_validate(
                model, X_train, y_train,
                cv=cv, scoring=["f1", "accuracy", "precision", "recall"],
                n_jobs=1, return_train_score=False
            )

            # ── Full fit ──────────────────────────────────────────────────────
            model.fit(X_train, y_train)
            elapsed = time.perf_counter() - t0

            # ── Validation metrics ────────────────────────────────────────────
            y_pred = model.predict(X_val)
            from sklearn.metrics import (accuracy_score, f1_score,
                                         precision_score, recall_score)
            val_acc  = accuracy_score(y_val, y_pred)
            val_f1   = f1_score(y_val, y_pred)
            val_prec = precision_score(y_val, y_pred)
            val_rec  = recall_score(y_val, y_pred)

            self.results_[name] = {
                "val_accuracy" : round(val_acc,  4),
                "val_f1"       : round(val_f1,   4),
                "val_precision": round(val_prec, 4),
                "val_recall"   : round(val_rec,  4),
                "cv_f1_mean"   : round(cv_scores["test_f1"].mean(), 4),
                "cv_f1_std"    : round(cv_scores["test_f1"].std(),  4),
                "cv_acc_mean"  : round(cv_scores["test_accuracy"].mean(), 4),
                "train_time_s" : round(elapsed, 2),
            }
            self.models_[name] = model
            save_model(model, name)

            logger.info(
                f"  {name}: Val-F1={val_f1:.4f}  CV-F1={self.results_[name]['cv_f1_mean']:.4f}"
                f"±{self.results_[name]['cv_f1_std']:.4f}  Time={elapsed:.1f}s"
            )

        return self.results_
