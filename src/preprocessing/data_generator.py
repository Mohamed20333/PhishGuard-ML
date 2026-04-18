"""
Synthetic Dataset Generator
============================
Generates a realistic phishing/legitimate URL dataset for demonstration
when the Kaggle dataset is not available locally.

Statistical properties are calibrated from:
- Sahingoz et al. (2019): "Machine learning based phishing detection"
- Mohammad et al. (2014): "Predicting Phishing Websites" (UCI dataset statistics)
"""

import numpy as np
import pandas as pd
import random
import string
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.config import RANDOM_STATE, SUSPICIOUS_WORDS, URL_SHORTENERS

np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)

# ── Legitimate URL templates ──────────────────────────────────────────────────
LEGIT_DOMAINS = [
    "google.com", "microsoft.com", "amazon.com", "github.com", "stackoverflow.com",
    "wikipedia.org", "bbc.co.uk", "nytimes.com", "apple.com", "linkedin.com",
    "twitter.com", "facebook.com", "youtube.com", "reddit.com", "netflix.com",
    "dropbox.com", "adobe.com", "salesforce.com", "shopify.com", "stripe.com",
    "cloudflare.com", "digitalocean.com", "heroku.com", "medium.com", "quora.com",
]
LEGIT_PATHS = [
    "/", "/about", "/contact", "/products", "/services", "/blog",
    "/docs/getting-started", "/help/faq", "/support", "/news/latest",
    "/api/v1/users", "/search?q=python", "/profile/settings", "/dashboard",
    "/learn/tutorial", "/download", "/pricing", "/careers", "/terms",
]

# ── Phishing URL templates ────────────────────────────────────────────────────
PHISH_PATTERNS = [
    "secure-{brand}-login.{tld}/{path}",
    "{brand}-account-verify.{tld}/{path}",
    "www.{brand}.account-update.{tld}/{path}",
    "{ip}/{brand}/login.php",
    "{short}/abc123",
    "{random}.{tld}/paypal/secure/login.php",
    "193.{r}.{r}.{r}/{brand}-login",
    "{brand}-secure.{suspicious_tld}/verify/{token}",
    "support-{brand}.{tld}/update-account/{token}",
    "login.{brand}-official.{suspicious_tld}/auth",
]
PHISH_BRANDS   = ["paypal", "amazon", "microsoft", "apple", "google", "netflix", "ebay", "facebook"]
SUSPICIOUS_TLD = [".tk", ".ml", ".ga", ".xyz", ".top", ".online", ".click", ".info"]
LEGIT_TLD      = [".com", ".net", ".org"]
PHISH_PATHS    = [
    "login.php", "signin", "verify-account", "secure/update",
    "account/confirm", "billing/update", "webscr?cmd=_login",
    "password/reset?token=", "auth/validate",
]


def _rand_str(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def _generate_legitimate_urls(n: int) -> list:
    urls = []
    for _ in range(n):
        domain = random.choice(LEGIT_DOMAINS)
        path   = random.choice(LEGIT_PATHS)
        scheme = "https://" if random.random() > 0.1 else "http://"
        urls.append(f"{scheme}{domain}{path}")
    return urls


def _generate_phishing_urls(n: int) -> list:
    urls = []
    for _ in range(n):
        pattern = random.choice(PHISH_PATTERNS)
        brand   = random.choice(PHISH_BRANDS)
        path    = random.choice(PHISH_PATHS)
        r       = str(random.randint(1, 254))
        ip      = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
        suspicious_tld = random.choice(SUSPICIOUS_TLD)
        tld     = random.choice(LEGIT_TLD)
        short   = random.choice(URL_SHORTENERS)
        token   = _rand_str(16)

        url = pattern.format(
            brand=brand, path=path, tld=tld.lstrip("."),
            ip=ip, short=short, r=r, suspicious_tld=suspicious_tld.lstrip("."),
            token=token, random=_rand_str(random.randint(8, 20))
        )
        # Prepend scheme randomly
        if not url.startswith("http"):
            url = ("http://" if random.random() > 0.3 else "https://") + url
        urls.append(url)
    return urls


def generate_dataset(n_legit: int = 5000, n_phish: int = 5000) -> pd.DataFrame:
    """
    Generate a balanced synthetic dataset.

    Returns
    -------
    pd.DataFrame with columns: ['url', 'label']
        label = 0 → legitimate, label = 1 → phishing
    """
    legit_urls = _generate_legitimate_urls(n_legit)
    phish_urls = _generate_phishing_urls(n_phish)

    df = pd.DataFrame({
        "url"  : legit_urls + phish_urls,
        "label": [0] * n_legit + [1] * n_phish,
    })
    return df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def generate_noisy_dataset(n_legit: int = 4000, n_phish: int = 4000) -> pd.DataFrame:
    """
    Generate a harder dataset with ambiguous cases for realistic evaluation.
    Includes edge cases: HTTPS phishing, legitimate-looking phishing, short legit URLs.
    """
    np.random.seed(RANDOM_STATE); random.seed(RANDOM_STATE)
    # Base dataset
    df = generate_dataset(n_legit, n_phish)

    # Add HTTPS phishing (harder cases)
    extra_phish = [
        f"https://secure-{b}-login.com/verify" for b in PHISH_BRANDS[:10]
    ] * 80
    extra_phish += [f"https://www.{b}-support.net/account" for b in PHISH_BRANDS] * 40

    # Add legitimate short URLs that look suspicious
    extra_legit = [
        "https://t.co/news123", "https://is.gd/techblog",
        "https://bit.ly/official-docs",
    ] * 30

    noisy = pd.DataFrame({
        "url"  : extra_phish + extra_legit,
        "label": [1]*len(extra_phish) + [0]*len(extra_legit),
    })
    combined = pd.concat([df, noisy], ignore_index=True)
    return combined.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
