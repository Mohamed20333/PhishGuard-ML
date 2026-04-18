"""
Feature Engineering — URL-Based Features
=========================================
Extracts 23 lexical, host-based, and structural features from raw URLs.
Each feature is motivated by real-world phishing characteristics documented
in the literature (Sahingoz et al. 2019; Zouina & Outtaj 2017).
"""

import re
import math
import urllib.parse
from collections import Counter
from typing import Dict

import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.config import SUSPICIOUS_WORDS, URL_SHORTENERS


# ── Helper functions ──────────────────────────────────────────────────────────

def _entropy(s: str) -> float:
    """Shannon entropy of a string — phishing URLs tend to be more random."""
    if not s:
        return 0.0
    counts = Counter(s)
    total = len(s)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _has_ip_address(url: str) -> int:
    """1 if the host is an IPv4 address (common in phishing)."""
    ip_pattern = re.compile(
        r"(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)"
    )
    return int(bool(ip_pattern.search(url)))


def _get_tld_risk(hostname: str) -> int:
    """
    0 = trusted TLD (.com, .org, .net, .edu, .gov)
    1 = medium-risk TLD
    2 = high-risk / unusual TLD
    Based on Spamhaus TLD reputation data.
    """
    trusted = {".com", ".org", ".net", ".edu", ".gov", ".co.uk", ".ac.uk"}
    high_risk = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
                 ".info", ".biz", ".club", ".online", ".site", ".click"}
    for tld in trusted:
        if hostname.endswith(tld):
            return 0
    for tld in high_risk:
        if hostname.endswith(tld):
            return 2
    return 1


# ── Core extractor ────────────────────────────────────────────────────────────

def extract_url_features(url: str) -> Dict[str, float]:
    """
    Extract 23 features from a URL string.

    Parameters
    ----------
    url : str
        Raw URL (with or without scheme).

    Returns
    -------
    dict : feature_name → value
    """
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        parsed = urllib.parse.urlparse("http://unknown.com")

    hostname = parsed.hostname or ""
    path     = parsed.path or ""
    query    = parsed.query or ""
    netloc   = parsed.netloc or ""

    # Remove 'www.' for subdomain counting
    clean_host = re.sub(r"^www\.", "", hostname)
    subdomains  = clean_host.split(".")
    domain_part = subdomains[-2] if len(subdomains) >= 2 else clean_host

    features: Dict[str, float] = {
        # ── Length-based ──────────────────────────────────────────────────────
        "url_length"       : len(url),
        "hostname_length"  : len(hostname),
        "path_length"      : len(path),
        "query_length"     : len(query),

        # ── Character-count features ──────────────────────────────────────────
        "num_dots"         : url.count("."),
        "num_hyphens"      : url.count("-"),
        "num_underscores"  : url.count("_"),
        "num_slashes"      : url.count("/"),
        "num_special_chars": len(re.findall(r"[!@#$%^&*()+=\[\]{};':\"\\|,<>/?]", url)),
        "num_digits"       : sum(c.isdigit() for c in url),
        "num_at_symbols"   : url.count("@"),

        # ── Structural / hostname features ────────────────────────────────────
        "num_subdomains"      : max(0, len(subdomains) - 2),
        "domain_length"       : len(domain_part),
        "prefix_suffix_domain": int("-" in domain_part),
        "tld_risk"            : _get_tld_risk(hostname),

        # ── Protocol / security indicators ───────────────────────────────────
        "has_https"        : int(parsed.scheme == "https"),
        "has_ip_address"   : _has_ip_address(url),
        "has_double_slash" : int("//" in path),

        # ── Lexical / content features ────────────────────────────────────────
        "has_suspicious_words": int(
            any(w in url.lower() for w in SUSPICIOUS_WORDS)
        ),
        "is_url_shortener" : int(
            any(s in hostname for s in URL_SHORTENERS)
        ),

        # ── Statistical features ──────────────────────────────────────────────
        "digit_ratio"      : sum(c.isdigit() for c in url) / max(len(url), 1),
        "uppercase_ratio"  : sum(c.isupper() for c in url) / max(len(url), 1),
        "url_entropy"      : _entropy(url),
    }

    return features


def extract_features_batch(urls: pd.Series) -> pd.DataFrame:
    """
    Extract features for a Series of URLs.
    Returns a DataFrame with 23 feature columns.
    """
    rows = [extract_url_features(u) for u in urls]
    return pd.DataFrame(rows)
