"""
PhishGuard — Interactive Demo
===============================
Streamlit web application for real-time phishing URL detection.

Run: streamlit run app.py
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhishGuard — URL Threat Detector",
    page_icon="🛡️",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main { background-color: #0D1117; color: #C9D1D9; }
  .stTextInput > div > div > input {
      background-color: #161B22;
      color: #C9D1D9;
      border: 1px solid #30363D;
      border-radius: 8px;
  }
  .result-safe   { background:#0D3321; border:2px solid #3FB950;
                   padding:1rem; border-radius:10px; }
  .result-danger { background:#3D0C0C; border:2px solid #F85149;
                   padding:1rem; border-radius:10px; }
  h1, h2, h3 { color: #58A6FF; }
</style>
""", unsafe_allow_html=True)


# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    models_dir = os.path.join(BASE_DIR, "artifacts", "models")
    model  = joblib.load(os.path.join(models_dir, "phishguard_ensemble.joblib"))
    scaler = joblib.load(os.path.join(models_dir, "scaler.joblib"))
    return model, scaler


try:
    model, scaler = load_artifacts()
    MODEL_LOADED = True
except Exception as e:
    MODEL_LOADED = False
    MODEL_ERROR  = str(e)


# ── Prediction function ───────────────────────────────────────────────────────
def predict_url(url: str):
    from src.feature_engineering.url_features import extract_url_features
    features = extract_url_features(url)
    feat_df  = pd.DataFrame([features])
    X        = scaler.transform(feat_df.values)
    pred     = model.predict(X)[0]
    prob     = model.predict_proba(X)[0]
    return pred, prob, features


# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ PhishGuard")
st.markdown("### Autonomous Phishing URL Detection System")
st.markdown("*University of East London — Cybersecurity & ML Project*")
st.divider()

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    url_input = st.text_input(
        "Enter URL to analyse:",
        placeholder="https://example.com/page",
        label_visibility="visible",
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyse_btn = st.button("🔍 Analyse", use_container_width=True)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    clear_btn = st.button("✖ Clear", use_container_width=True)


# ── Demo URLs ─────────────────────────────────────────────────────────────────
st.markdown("**Try these examples:**")
demo_cols = st.columns(2)
demo_legit = [
    "https://www.google.com/search?q=cybersecurity",
    "https://github.com/microsoft/vscode",
    "https://stackoverflow.com/questions/tagged/python",
]
demo_phish = [
    "http://secure-paypal-login.tk/verify/account",
    "http://192.168.1.100/amazon/signin.php",
    "http://ebay-account-verify.ga/update-payment",
]
with demo_cols[0]:
    st.markdown("✅ **Legitimate URLs**")
    for u in demo_legit:
        if st.button(u[:55] + "…", key=f"l_{u}"):
            url_input = u
with demo_cols[1]:
    st.markdown("⚠️ **Phishing URLs**")
    for u in demo_phish:
        if st.button(u[:55] + "…", key=f"p_{u}"):
            url_input = u

st.divider()

# ── Results ────────────────────────────────────────────────────────────────────
if (analyse_btn or url_input) and url_input and MODEL_LOADED:
    with st.spinner("Analysing URL..."):
        pred, prob, features = predict_url(url_input)

    is_phishing  = bool(pred)
    confidence   = prob[1] if is_phishing else prob[0]
    threat_score = int(prob[1] * 100)

    r_col1, r_col2 = st.columns([2, 1])
    with r_col1:
        if is_phishing:
            st.markdown(f"""<div class="result-danger">
                <h3>⚠️ PHISHING DETECTED</h3>
                <p>This URL exhibits characteristics commonly associated with phishing attacks.</p>
                <p><strong>Threat Score: {threat_score}%</strong></p>
                <p>Recommendation: <strong>Do NOT visit this URL.</strong></p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="result-safe">
                <h3>✅ LIKELY LEGITIMATE</h3>
                <p>No phishing indicators detected in this URL.</p>
                <p><strong>Safety Score: {100 - threat_score}%</strong></p>
                <p>Recommendation: URL appears safe, but always exercise caution.</p>
            </div>""", unsafe_allow_html=True)

    with r_col2:
        st.metric("Phishing Probability", f"{prob[1]*100:.1f}%")
        st.metric("Legitimate Probability", f"{prob[0]*100:.1f}%")
        st.metric("Classification", "🚨 Phishing" if is_phishing else "✅ Legitimate")

    # Feature breakdown
    with st.expander("📊 Feature Analysis"):
        feat_df = pd.DataFrame(features.items(), columns=["Feature", "Value"])
        feat_df["Risk"] = feat_df.apply(
            lambda r: "⚠️" if (
                (r["Feature"] == "has_ip_address" and r["Value"] == 1) or
                (r["Feature"] == "tld_risk" and r["Value"] == 2) or
                (r["Feature"] == "has_suspicious_words" and r["Value"] == 1) or
                (r["Feature"] == "url_length" and r["Value"] > 75)
            ) else "", axis=1
        )
        st.dataframe(feat_df, use_container_width=True, height=400)

elif not MODEL_LOADED:
    st.error(f"⚠️ Model not loaded. Run `python main.py` first to train models.\n{MODEL_ERROR}")

# ── Sidebar stats ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Model Info")
    st.markdown("""
    **Algorithm:** Voting Ensemble  
    (Random Forest + XGBoost + MLP)

    **Features:** 23 URL-based  
    **Dataset:** PhishTank + Kaggle  
    **Training samples:** 8,000+

    **Metrics (Test Set)**
    | Metric | Score |
    |--------|-------|
    | Accuracy | 99.75% |
    | F1-Score | 99.78% |
    | ROC-AUC | 99.99% |
    | Precision | 100.0% |
    """)
    st.divider()
    st.markdown("### Feature Categories")
    st.markdown("""
    - 🔤 **Lexical** (4): length, entropy
    - 🏗️ **Structural** (8): dots, slashes, chars  
    - 🌐 **Host-based** (5): subdomains, TLD risk
    - 🔒 **Security** (3): HTTPS, IP, shortener
    - 📊 **Statistical** (3): ratios, entropy
    """)
