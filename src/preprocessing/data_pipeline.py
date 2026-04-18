"""
Data Loader & Preprocessor
===========================
Handles loading from Kaggle CSV or generating synthetic data,
then applies a full preprocessing pipeline.
"""

import os
import joblib
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing   import StandardScaler
from imblearn.over_sampling  import SMOTE
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.config            import (RANDOM_STATE, TEST_SIZE, VAL_SIZE,
                                      TARGET_COL, PROCESSED, MODELS_DIR)
from src.preprocessing.data_generator  import generate_dataset
from src.feature_engineering.url_features import extract_features_batch

logger = logging.getLogger(__name__)


class PhishGuardDataPipeline:
    """
    End-to-end data pipeline:
      1. Load raw data (CSV or synthetic)
      2. Extract URL features
      3. Handle missing values & outliers
      4. Train/val/test split
      5. Scale features
      6. SMOTE oversampling (train set only)
    """

    def __init__(self):
        self.scaler    : StandardScaler | None = None
        self.feature_names: list = []

    # ── Loading ───────────────────────────────────────────────────────────────

    def load(self, csv_path: str | None = None,
             n_legit: int = 5000, n_phish: int = 5000) -> pd.DataFrame:
        """
        Load data from CSV or generate synthetic dataset.
        Expected CSV columns: 'url' (str) and 'label' (0/1).
        """
        if csv_path and os.path.exists(csv_path):
            logger.info(f"Loading dataset from {csv_path}")
            df = pd.read_csv(csv_path)
            # Normalize label column name
            df.columns = [c.lower().strip() for c in df.columns]
            if "class" in df.columns:
                df.rename(columns={"class": TARGET_COL}, inplace=True)
        else:
            logger.info("CSV not found — generating synthetic dataset for demonstration")
            df = generate_dataset(n_legit=n_legit, n_phish=n_phish)

        logger.info(f"Loaded {len(df):,} records | "
                    f"Phishing: {df[TARGET_COL].sum():,} | "
                    f"Legitimate: {(df[TARGET_COL] == 0).sum():,}")
        return df

    # ── Feature extraction ────────────────────────────────────────────────────

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract URL features and append to dataframe."""
        logger.info("Extracting URL features...")
        feat_df = extract_features_batch(df["url"])
        self.feature_names = feat_df.columns.tolist()
        out = pd.concat([df.reset_index(drop=True), feat_df], axis=1)
        logger.info(f"Extracted {len(self.feature_names)} features")
        return out

    # ── Preprocessing ──────────────────────────────────────────────────────────

    def preprocess(self, df: pd.DataFrame):
        """
        Full preprocessing pipeline.

        Returns
        -------
        X_train, X_val, X_test, y_train, y_val, y_test  (all np.ndarray)
        Also saves scaler to MODELS_DIR.
        """
        # Drop original URL string
        feature_cols = self.feature_names
        X = df[feature_cols].values
        y = df[TARGET_COL].values

        # ── Check for NaN/Inf ─────────────────────────────────────────────────
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        # ── Train / val / test split (70 / 15 / 15) ───────────────────────────
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
        )
        val_frac = VAL_SIZE / (1 - TEST_SIZE)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_frac, stratify=y_temp,
            random_state=RANDOM_STATE
        )

        # ── Feature scaling ───────────────────────────────────────────────────
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_val   = self.scaler.transform(X_val)
        X_test  = self.scaler.transform(X_test)

        # ── SMOTE (applied only to train set) ─────────────────────────────────
        class_counts = pd.Series(y_train).value_counts()
        if class_counts.min() / class_counts.max() < 0.9:
            logger.info("Applying SMOTE to balance training set...")
            smote = SMOTE(random_state=RANDOM_STATE)
            X_train, y_train = smote.fit_resample(X_train, y_train)
            logger.info(f"Post-SMOTE training size: {len(y_train):,}")

        # ── Save scaler ───────────────────────────────────────────────────────
        os.makedirs(MODELS_DIR, exist_ok=True)
        scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Scaler saved → {scaler_path}")

        logger.info(f"Split sizes  — Train: {len(y_train):,} | "
                    f"Val: {len(y_val):,} | Test: {len(y_test):,}")

        # ── Save processed splits ─────────────────────────────────────────────
        os.makedirs(PROCESSED, exist_ok=True)
        for name, arr in [("X_train", X_train), ("X_val", X_val), ("X_test", X_test),
                           ("y_train", y_train), ("y_val", y_val), ("y_test", y_test)]:
            np.save(os.path.join(PROCESSED, f"{name}.npy"), arr)

        return X_train, X_val, X_test, y_train, y_val, y_test

    def run(self, csv_path=None, n_legit=5000, n_phish=5000):
        """Convenience: load → extract → preprocess in one call."""
        df = self.load(csv_path, n_legit=n_legit, n_phish=n_phish)
        df = self.extract_features(df)
        return df, self.preprocess(df)
