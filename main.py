"""
PhishGuard — Main Pipeline
===========================
Run this script to execute the full ML pipeline end-to-end:
  1. Data generation / loading
  2. Feature extraction (23 URL-based features)
  3. Preprocessing (scaling, SMOTE)
  4. Model training (5 classifiers + ensemble)
  5. Evaluation (test set metrics)
  6. Visualization (10 figures)
  7. Results export

Usage
-----
    python main.py                        # use synthetic data
    python main.py --csv data/raw/phishing.csv   # use Kaggle CSV

Author : Mohamed Elsharkawy — University of East London
Project: PhishGuard — Autonomous Phishing URL Detection System
"""

import argparse
import logging
import os
import sys
import json

import numpy as np
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config.config import PLOTS_DIR, MODELS_DIR, REPORTS_DIR
from src.preprocessing.data_pipeline  import PhishGuardDataPipeline
from src.training.trainer              import ModelTrainer
from src.evaluation.metrics            import evaluate_all, comparison_table
from src.evaluation.visualizer         import (
    plot_class_distribution, plot_feature_distributions,
    plot_correlation_heatmap, plot_feature_importance,
    plot_model_comparison, plot_roc_curves,
    plot_confusion_matrix, plot_pr_curves,
    plot_cv_results, plot_inference_time,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PhishGuard")


def parse_args():
    p = argparse.ArgumentParser(description="PhishGuard ML Pipeline")
    p.add_argument("--csv",    type=str, default=None,
                   help="Path to Kaggle CSV (optional)")
    p.add_argument("--legit",  type=int, default=5000,
                   help="Synthetic legitimate URLs (default 5000)")
    p.add_argument("--phish",  type=int, default=5000,
                   help="Synthetic phishing URLs (default 5000)")
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(PLOTS_DIR,   exist_ok=True)
    os.makedirs(MODELS_DIR,  exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    logger.info("=" * 60)
    logger.info("PhishGuard — Phishing URL Detection System")
    logger.info("=" * 60)

    # ── 1. Data Pipeline ──────────────────────────────────────────────────────
    pipeline = PhishGuardDataPipeline()
    df, (X_train, X_val, X_test, y_train, y_val, y_test) = pipeline.run(
        csv_path=args.csv, n_legit=args.legit, n_phish=args.phish
    )
    feature_names = pipeline.feature_names

    # ── 2. EDA Visualizations ─────────────────────────────────────────────────
    logger.info("Generating EDA visualizations...")
    plot_class_distribution(df["label"].values)
    plot_feature_distributions(df, feature_names)
    plot_correlation_heatmap(df, feature_names)

    # ── 3. Training ───────────────────────────────────────────────────────────
    trainer = ModelTrainer()
    train_results = trainer.train_all(X_train, y_train, X_val, y_val)

    # ── 4. Evaluation ─────────────────────────────────────────────────────────
    logger.info("Evaluating all models on test set...")
    all_results = evaluate_all(trainer.models_, X_test, y_test)

    # ── 5. Model visualizations ───────────────────────────────────────────────
    logger.info("Generating model evaluation plots...")

    # Feature importance from RF
    rf_model = trainer.models_.get("Random Forest")
    if rf_model:
        plot_feature_importance(rf_model, feature_names)

    plot_model_comparison(all_results)
    plot_roc_curves(all_results)
    plot_pr_curves(all_results)
    plot_cv_results(train_results)
    plot_inference_time(all_results)

    # Confusion matrix for best model (ensemble)
    best_key = "PhishGuard Ensemble"
    if best_key in all_results:
        plot_confusion_matrix(all_results[best_key])

    # ── 6. Comparison Table ───────────────────────────────────────────────────
    comp_df = comparison_table(all_results)
    logger.info("\n" + comp_df.to_string())

    # ── 7. Save Results JSON ──────────────────────────────────────────────────
    summary = {}
    for name, r in all_results.items():
        summary[name] = {
            k: float(v) if isinstance(v, (np.floating, float)) else v
            for k, v in r.items()
            if k not in ("confusion_matrix", "class_report",
                         "fpr", "tpr", "precision_curve", "recall_curve")
        }
        summary[name]["cv_f1_mean"] = float(train_results[name]["cv_f1_mean"])
        summary[name]["cv_f1_std"]  = float(train_results[name]["cv_f1_std"])
        summary[name]["train_time"] = float(train_results[name]["train_time_s"])

    results_path = os.path.join(REPORTS_DIR, "results_summary.json")
    with open(results_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Results saved → {results_path}")

    # ── 8. Sample Predictions ─────────────────────────────────────────────────
    test_urls = [
        "https://www.google.com/search?q=python",
        "http://secure-paypal-login.tk/verify/account",
        "https://github.com/user/repo",
        "http://192.168.1.100/amazon/signin.php",
        "https://www.microsoft.com/en-us/security",
        "http://paypal-secure.xyz/login?redirect=billing",
        "https://stackoverflow.com/questions/12345",
        "http://bit.ly/3xK9mPq",
        "https://www.bbc.co.uk/news/technology",
        "http://ebay-account-verify.ga/update-payment",
    ]
    true_labels = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

    best_model  = trainer.models_[best_key]
    scaler      = pipeline.scaler
    from src.feature_engineering.url_features import extract_features_batch
    feat_df  = extract_features_batch(pd.Series(test_urls))
    feat_arr = scaler.transform(feat_df.values)
    preds    = best_model.predict(feat_arr)
    probs    = best_model.predict_proba(feat_arr)[:, 1]

    pred_df = pd.DataFrame({
        "URL"          : test_urls,
        "True Label"   : ["Phishing" if l else "Legitimate" for l in true_labels],
        "Predicted"    : ["Phishing" if p else "Legitimate" for p in preds],
        "Confidence"   : [f"{p:.2%}" for p in probs],
        "Correct"      : ["✓" if p == t else "✗" for p, t in zip(preds, true_labels)],
    })

    sample_path = os.path.join(REPORTS_DIR, "sample_predictions.csv")
    pred_df.to_csv(sample_path, index=False)
    logger.info(f"\n{pred_df.to_string(index=False)}")
    logger.info(f"Sample predictions saved → {sample_path}")

    # ── Done ──────────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("Pipeline complete!")
    logger.info(f"Best model (PhishGuard Ensemble): "
                f"F1={all_results[best_key]['f1']:.4f}  "
                f"ROC-AUC={all_results[best_key]['roc_auc']:.4f}")
    logger.info(f"Plots saved to   : {PLOTS_DIR}")
    logger.info(f"Models saved to  : {MODELS_DIR}")
    logger.info("=" * 60)

    return all_results


if __name__ == "__main__":
    main()
