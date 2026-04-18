"""
Evaluation Module — PhishGuard
================================
Computes comprehensive metrics: classification report, ROC-AUC,
PR-AUC, confusion matrix, and inference benchmarks.
"""

import time
import logging
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, average_precision_score,
    roc_curve, precision_recall_curve, f1_score,
    accuracy_score, precision_score, recall_score,
)
from scipy import stats

logger = logging.getLogger(__name__)


def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray,
                   model_name: str = "Model") -> dict:
    """
    Full evaluation of a single model on the test set.

    Returns
    -------
    dict with keys: accuracy, precision, recall, f1, roc_auc,
                    pr_auc, confusion_matrix, class_report,
                    inference_time_ms, fpr, tpr, thresholds_roc,
                    prec_curve, rec_curve
    """
    # ── Predictions ────────────────────────────────────────────────────────────
    t0     = time.perf_counter()
    y_pred = model.predict(X_test)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    y_prob = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, "predict_proba") else
        model.decision_function(X_test)
    )

    # ── Core metrics ───────────────────────────────────────────────────────────
    cm     = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred,
                                   target_names=["Legitimate", "Phishing"],
                                   output_dict=True)
    roc_auc = roc_auc_score(y_test, y_prob)
    pr_auc  = average_precision_score(y_test, y_prob)

    # ── Curves ─────────────────────────────────────────────────────────────────
    fpr, tpr, thr_roc  = roc_curve(y_test, y_prob)
    prec, rec, thr_pr  = precision_recall_curve(y_test, y_prob)

    result = {
        "model_name"       : model_name,
        "accuracy"         : round(accuracy_score(y_test, y_pred), 4),
        "precision"        : round(precision_score(y_test, y_pred), 4),
        "recall"           : round(recall_score(y_test, y_pred), 4),
        "f1"               : round(f1_score(y_test, y_pred), 4),
        "roc_auc"          : round(roc_auc, 4),
        "pr_auc"           : round(pr_auc, 4),
        "confusion_matrix" : cm,
        "class_report"     : report,
        "inference_time_ms": round(elapsed_ms / len(y_test), 4),
        "fpr"              : fpr,
        "tpr"              : tpr,
        "precision_curve"  : prec,
        "recall_curve"     : rec,
    }

    logger.info(
        f"{model_name}: Acc={result['accuracy']:.4f}  "
        f"F1={result['f1']:.4f}  ROC-AUC={result['roc_auc']:.4f}  "
        f"PR-AUC={result['pr_auc']:.4f}  "
        f"Latency={result['inference_time_ms']:.4f}ms/sample"
    )
    return result


def evaluate_all(models: dict, X_test: np.ndarray,
                 y_test: np.ndarray) -> dict:
    """Evaluate every model and return results dict."""
    return {name: evaluate_model(m, X_test, y_test, name)
            for name, m in models.items()}


def comparison_table(all_results: dict) -> pd.DataFrame:
    """Build a formatted comparison DataFrame for reporting."""
    rows = []
    for name, r in all_results.items():
        rows.append({
            "Model"           : name,
            "Accuracy"        : r["accuracy"],
            "Precision"       : r["precision"],
            "Recall"          : r["recall"],
            "F1-Score"        : r["f1"],
            "ROC-AUC"         : r["roc_auc"],
            "PR-AUC"          : r["pr_auc"],
            "Latency (ms)"    : r["inference_time_ms"],
        })
    df = pd.DataFrame(rows).set_index("Model")
    return df.sort_values("F1-Score", ascending=False)
