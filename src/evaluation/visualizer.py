"""
Visualization Module — PhishGuard
===================================
Generates ALL required figures (8+) in a consistent dark cybersecurity theme.

Figures produced:
  1.  class_distribution.png        — class imbalance bar chart
  2.  feature_distributions.png     — histograms of key features
  3.  correlation_heatmap.png       — feature correlation matrix
  4.  feature_importance.png        — RF + XGB importance (horizontal bar)
  5.  model_comparison.png          — grouped bar: Acc/F1/ROC-AUC
  6.  roc_curves.png                — multi-model ROC curves
  7.  confusion_matrix_ensemble.png — heatmap for best model
  8.  precision_recall_curve.png    — PR curves
  9.  cv_results.png                — cross-validation F1 box/bar
  10. inference_time.png            — latency comparison
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.config import PLOTS_DIR, PALETTE, DPI

logger = logging.getLogger(__name__)

# ── Theme setup ────────────────────────────────────────────────────────────────
def _apply_theme():
    plt.rcParams.update({
        "figure.facecolor"  : PALETTE["dark_bg"],
        "axes.facecolor"    : PALETTE["panel"],
        "axes.edgecolor"    : PALETTE["grid"],
        "axes.labelcolor"   : PALETTE["text"],
        "xtick.color"       : PALETTE["text"],
        "ytick.color"       : PALETTE["text"],
        "text.color"        : PALETTE["text"],
        "grid.color"        : PALETTE["grid"],
        "grid.linestyle"    : "--",
        "grid.alpha"        : 0.5,
        "font.family"       : "DejaVu Sans",
        "font.size"         : 10,
        "axes.titlesize"    : 13,
        "axes.titleweight"  : "bold",
        "legend.facecolor"  : PALETTE["panel"],
        "legend.edgecolor"  : PALETTE["grid"],
        "legend.labelcolor" : PALETTE["text"],
    })

_apply_theme()
os.makedirs(PLOTS_DIR, exist_ok=True)

MODEL_COLORS = {
    "Logistic Regression" : "#94A3B8",
    "Decision Tree"       : PALETTE["accent_gold"],
    "Random Forest"       : PALETTE["accent_green"],
    "XGBoost"             : PALETTE["accent_blue"],
    "MLP Neural Network"  : "#A78BFA",
    "PhishGuard Ensemble" : PALETTE["accent_red"],
}

# ── 1. Class Distribution ──────────────────────────────────────────────────────
def plot_class_distribution(y: np.ndarray) -> str:
    _apply_theme()
    fig, ax = plt.subplots(figsize=(6, 4))
    counts = pd.Series(y).value_counts().sort_index()
    labels = ["Legitimate", "Phishing"]
    colors = [PALETTE["accent_green"], PALETTE["accent_red"]]
    bars = ax.bar(labels, counts.values, color=colors, width=0.5,
                  edgecolor=PALETTE["grid"], linewidth=1.2)
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f"{val:,}\n({val/len(y)*100:.1f}%)",
                ha="center", va="bottom", fontsize=10, color=PALETTE["text"])
    ax.set_title("Class Distribution", pad=12)
    ax.set_ylabel("Count")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "01_class_distribution.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 2. Feature Distributions ──────────────────────────────────────────────────
def plot_feature_distributions(df: pd.DataFrame, feature_cols: list) -> str:
    _apply_theme()
    cols = ["url_length", "num_dots", "url_entropy", "num_subdomains",
            "digit_ratio", "has_suspicious_words"]
    cols = [c for c in cols if c in df.columns][:6]
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    axes = axes.flatten()
    label_col = "label"

    for i, col in enumerate(cols):
        ax = axes[i]
        for lbl, color, name in [(0, PALETTE["accent_green"], "Legitimate"),
                                   (1, PALETTE["accent_red"],   "Phishing")]:
            subset = df[df[label_col] == lbl][col].dropna()
            ax.hist(subset, bins=30, alpha=0.65, color=color, label=name,
                    edgecolor="none", density=True)
        ax.set_title(col.replace("_", " ").title())
        ax.legend(fontsize=8)
        ax.yaxis.grid(True)
        ax.set_axisbelow(True)

    fig.suptitle("Feature Distributions: Phishing vs Legitimate",
                 fontsize=14, y=1.01)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "02_feature_distributions.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 3. Correlation Heatmap ────────────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame, feature_cols: list) -> str:
    _apply_theme()
    corr = df[feature_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig, ax = plt.subplots(figsize=(12, 9))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(corr, mask=mask, cmap=cmap, center=0, vmin=-1, vmax=1,
                annot=False, linewidths=0.4, linecolor=PALETTE["dark_bg"],
                ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Matrix", pad=12)
    ax.tick_params(labelsize=7, rotation=45)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "03_correlation_heatmap.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 4. Feature Importance ─────────────────────────────────────────────────────
def plot_feature_importance(rf_model, feature_names: list, top_n: int = 15) -> str:
    _apply_theme()
    importances = pd.Series(rf_model.feature_importances_, index=feature_names)
    top = importances.nlargest(top_n).sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [PALETTE["accent_blue"] if v > top.median() else "#4A5568"
              for v in top.values]
    ax.barh(top.index, top.values, color=colors, edgecolor="none", height=0.65)
    ax.set_xlabel("Importance Score (MDI)")
    ax.set_title(f"Top {top_n} Feature Importances — Random Forest")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "04_feature_importance.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 5. Model Comparison Bar Chart ─────────────────────────────────────────────
def plot_model_comparison(all_results: dict) -> str:
    _apply_theme()
    models  = list(all_results.keys())
    metrics = ["accuracy", "f1", "roc_auc"]
    labels  = ["Accuracy", "F1-Score", "ROC-AUC"]
    x       = np.arange(len(models))
    width   = 0.25
    colors  = [PALETTE["accent_blue"], PALETTE["accent_green"], PALETTE["accent_gold"]]

    fig, ax = plt.subplots(figsize=(14, 5))
    for i, (metric, label, color) in enumerate(zip(metrics, labels, colors)):
        vals = [all_results[m][metric] for m in models]
        bars = ax.bar(x + i * width, vals, width, label=label, color=color,
                      edgecolor="none", alpha=0.9)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.002,
                    f"{v:.3f}", ha="center", va="bottom", fontsize=7.5,
                    color=PALETTE["text"])

    ax.set_xticks(x + width)
    ax.set_xticklabels([m.replace(" ", "\n") for m in models], fontsize=9)
    ax.set_ylim(0.85, 1.02)
    ax.set_ylabel("Score")
    ax.set_title("Model Performance Comparison")
    ax.legend(loc="lower right")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    # Highlight ensemble
    best_idx = list(models).index("PhishGuard Ensemble") if "PhishGuard Ensemble" in models else -1
    if best_idx >= 0:
        ax.axvspan(best_idx - 0.05, best_idx + 3 * width + 0.1,
                   alpha=0.07, color=PALETTE["accent_red"])

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "05_model_comparison.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 6. ROC Curves ────────────────────────────────────────────────────────────
def plot_roc_curves(all_results: dict) -> str:
    _apply_theme()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([0, 1], [0, 1], "--", color="#4A5568", linewidth=1, label="Random")
    for name, r in all_results.items():
        color = MODEL_COLORS.get(name, PALETTE["accent_blue"])
        lw    = 2.5 if "Ensemble" in name else 1.5
        ax.plot(r["fpr"], r["tpr"], color=color, linewidth=lw,
                label=f"{name} (AUC={r['roc_auc']:.3f})")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — All Models")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "06_roc_curves.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 7. Confusion Matrix ───────────────────────────────────────────────────────
def plot_confusion_matrix(result: dict) -> str:
    _apply_theme()
    cm = result["confusion_matrix"]
    fig, ax = plt.subplots(figsize=(6, 5))
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "phish_cmap", [PALETTE["panel"], PALETTE["accent_blue"]])
    sns.heatmap(cm_norm, annot=cm, fmt="d", cmap=cmap, ax=ax,
                xticklabels=["Legitimate", "Phishing"],
                yticklabels=["Legitimate", "Phishing"],
                linewidths=1, linecolor=PALETTE["dark_bg"],
                cbar_kws={"format": "%.0%"})
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    ax.set_title(f"Confusion Matrix — {result['model_name']}")
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "07_confusion_matrix_ensemble.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 8. Precision-Recall Curves ───────────────────────────────────────────────
def plot_pr_curves(all_results: dict) -> str:
    _apply_theme()
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, r in all_results.items():
        color = MODEL_COLORS.get(name, PALETTE["accent_blue"])
        lw    = 2.5 if "Ensemble" in name else 1.5
        ax.plot(r["recall_curve"], r["precision_curve"], color=color,
                linewidth=lw, label=f"{name} (AP={r['pr_auc']:.3f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curves — All Models")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "08_precision_recall_curves.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 9. Cross-Validation Results ───────────────────────────────────────────────
def plot_cv_results(train_results: dict) -> str:
    _apply_theme()
    models = list(train_results.keys())
    means  = [train_results[m]["cv_f1_mean"] for m in models]
    stds   = [train_results[m]["cv_f1_std"]  for m in models]
    colors = [MODEL_COLORS.get(m, PALETTE["accent_blue"]) for m in models]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(models))
    ax.bar(x, means, yerr=stds, color=colors, capsize=5,
           edgecolor="none", alpha=0.85, error_kw={"color": PALETTE["text"]})
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace(" ", "\n") for m in models], fontsize=9)
    ax.set_ylim(0.85, 1.01)
    ax.set_ylabel("F1-Score")
    ax.set_title(f"5-Fold Stratified Cross-Validation F1-Score (mean ± std)")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "09_cv_results.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path


# ── 10. Inference Time ────────────────────────────────────────────────────────
def plot_inference_time(all_results: dict) -> str:
    _apply_theme()
    models    = list(all_results.keys())
    latencies = [all_results[m]["inference_time_ms"] for m in models]
    colors    = [MODEL_COLORS.get(m, PALETTE["accent_blue"]) for m in models]

    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.barh(models, latencies, color=colors, edgecolor="none", alpha=0.85)
    for bar, v in zip(bars, latencies):
        ax.text(bar.get_width() + 0.00005,
                bar.get_y() + bar.get_height()/2,
                f"{v:.5f} ms", va="center", fontsize=9,
                color=PALETTE["text"])
    ax.set_xlabel("Inference Time per Sample (ms)")
    ax.set_title("Per-Sample Inference Latency")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "10_inference_time.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=PALETTE["dark_bg"])
    plt.close(fig)
    logger.info(f"Saved: {path}")
    return path
