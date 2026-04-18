# 🛡️ PhishGuard — Phishing URL Detection System

> **University of East London | BSc Cybersecurity & Networks**  
> Mohamed Elsharkawy (u3293254) | Cybersecurity Machine Learning Project

---

## Overview

PhishGuard is an autonomous machine learning system that classifies URLs as **phishing** or **legitimate** using 23 lexical, host-based, and statistical features. The system implements five ML algorithms alongside a **Voting Ensemble** (Random Forest + XGBoost + MLP Neural Network).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full pipeline (with synthetic demo data)
python main.py

# 3. Run with real Kaggle dataset
python main.py --csv data/raw/phishing.csv

# 4. Launch interactive demo
streamlit run app.py
```

## Project Structure

```
PhishGuard/
├── config/config.py              # Central configuration
├── src/
│   ├── preprocessing/
│   │   ├── data_pipeline.py      # Load → extract → split → scale
│   │   └── data_generator.py     # Synthetic dataset for demo
│   ├── feature_engineering/
│   │   └── url_features.py       # 23 URL feature extractor
│   ├── models/
│   │   └── classifiers.py        # All 5 models + ensemble
│   ├── training/
│   │   └── trainer.py            # Training + cross-validation
│   └── evaluation/
│       ├── metrics.py            # Comprehensive evaluation
│       └── visualizer.py         # 10 publication-quality figures
├── main.py                       # Full pipeline runner
├── app.py                        # Streamlit interactive demo
├── requirements.txt
└── artifacts/
    ├── models/                   # Saved joblib model files
    └── plots/                    # 10 generated figures
```

## Features Extracted (23 total)

| Category | Features |
|----------|----------|
| Length-based | `url_length`, `hostname_length`, `path_length`, `query_length` |
| Character-count | `num_dots`, `num_hyphens`, `num_underscores`, `num_slashes`, `num_special_chars`, `num_digits`, `num_at_symbols` |
| Structural | `num_subdomains`, `domain_length`, `prefix_suffix_domain`, `tld_risk` |
| Security | `has_https`, `has_ip_address`, `has_double_slash` |
| Lexical | `has_suspicious_words`, `is_url_shortener` |
| Statistical | `digit_ratio`, `uppercase_ratio`, `url_entropy` |

## Models & Results

| Model | Accuracy | F1 | ROC-AUC |
|-------|----------|----|---------|
| Logistic Regression | 99.75% | 99.78% | 100.0% |
| Decision Tree | 100.0% | 100.0% | 100.0% |
| Random Forest | 100.0% | 100.0% | 100.0% |
| XGBoost | 100.0% | 100.0% | 100.0% |
| MLP Neural Network | 100.0% | 100.0% | 100.0% |
| **PhishGuard Ensemble** | **100.0%** | **100.0%** | **100.0%** |

> Results on synthetic dataset. On real Kaggle dataset, expected F1 ≈ 97–99% (literature).

## Dataset

- **Source:** Kaggle — [Phishing Dataset for Machine Learning](https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning)
- **Backup:** PhishTank public feed + synthetic generator (included)
- **Size:** 10,000+ samples | 50/50 balanced classes

## Author

**Mohamed Moslem Samy Elsharkawy**  
Student ID: u3293254 | BSc Cybersecurity & Networks  
University of East London (via European University in Egypt)  
Email: muslems2010s@gmail.com
