"""
OMEGA Realtime Safety & Guardrails Engine (Stage 4)
===================================================
Production-grade security layer for real-time web retrieval:
1. PII Redaction: Strips emails, phone numbers, Aadhaar, and national IDs from queries.
2. SSRF Protection: Blocks private IPs, loopbacks, link-local, and non-http(s) schemes in fetch_page.
3. Rate Limiting & Tavily Budget Tracker:
   - Per-user rate limits (10 req/min).
   - Global rate limits (60 req/min).
   - Monthly 1,000 free search budget tracking with an 80% (800) alert threshold.
4. Adversarial Injection & Key Exfiltration Shield:
   - Blocks fake system directives, credential exfiltration, and prompt extraction.
   - Output secret scrubber preventing API key / .env leakage.
"""

import os
import re
import json
import time
import socket
import logging
import ipaddress
from typing import Dict, Any, Tuple, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger("omega.realtime.safety")

# ==============================================================================
# 1. PII REDACTION ENGINE
# ==============================================================================
EMAIL_REGEX = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    re.IGNORECASE
)

# Phone regex covering Indian (+91, 10-digit), US (+1, 10-digit), hyphenated, parenthesized
PHONE_REGEX = re.compile(
    r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}\b'
)

# Indian Aadhaar 12-digit format
AADHAAR_REGEX = re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b')

# US SSN format
SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

# Credit / Debit Card numbers (13 to 19 digits with spaces or hyphens)
CREDIT_CARD_REGEX = re.compile(r'\b(?:\d{4}[-\s]?){3,4}\d{1,4}\b')

# Personal names in identification context (does NOT strip public-figure news queries)
NAME_CONTEXT_REGEX = re.compile(
    r'(?i)\b(?:my\s+name\s+is|i\s+am\s+named|i\'m\s+named|name\s*[:\-]\s*|'
    r'call\s+me|contact\s+(?:person\s+)?(?:is\s+)?)\s*'
    r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})'
)

# First Last when the same query already contains other PII
STANDALONE_NAME_REGEX = re.compile(
    r'\b([A-Z][a-z]{1,}(?:\s+[A-Z][a-z]{1,}){1,2})\b'
)

GEO_AND_COMMON_PROPER = {
    "new delhi", "delhi", "mumbai", "bengaluru", "bangalore", "chennai", "kolkata",
    "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow", "india", "maharashtra",
    "punjab", "gujarat", "karnataka", "rajasthan", "haryana", "bihar", "odisha",
    "united states", "united kingdom", "new york", "san francisco", "los angeles",
    "open meteo", "yahoo finance",
}


def scrub_pii(query: str) -> Tuple[str, List[str]]:
    """
    Remove personally identifiable information (PII) from queries before sending to search APIs.
    Returns: (cleaned_query, list_of_redactions)
    """
    if not query or not isinstance(query, str):
        return "", []

    redactions = []
    cleaned = query

    # 1. Scrub Emails
    emails_found = EMAIL_REGEX.findall(cleaned)
    if emails_found:
        redactions.extend([f"email:{e}" for e in emails_found])
        cleaned = EMAIL_REGEX.sub("[REDACTED_EMAIL]", cleaned)

    # 2. Scrub Aadhaar / SSN
    aadhaar_found = AADHAAR_REGEX.findall(cleaned)
    if aadhaar_found:
        redactions.extend(["aadhaar:****"])
        cleaned = AADHAAR_REGEX.sub("[REDACTED_ID]", cleaned)

    ssn_found = SSN_REGEX.findall(cleaned)
    if ssn_found:
        redactions.extend(["ssn:****"])
        cleaned = SSN_REGEX.sub("[REDACTED_ID]", cleaned)

    # 3. Scrub Credit Cards
    cards_found = CREDIT_CARD_REGEX.findall(cleaned)
    for c in cards_found:
        digits_only = re.sub(r'\D', '', c)
        if 13 <= len(digits_only) <= 19:
            redactions.append("card:****")
            cleaned = cleaned.replace(c, "[REDACTED_FINANCIAL]")

    # 4. Scrub Phone Numbers
    phone_candidates = PHONE_REGEX.findall(cleaned)
    for p in phone_candidates:
        digits_only = re.sub(r'\D', '', p)
        # Avoid matching small numbers or years like 2026
        if 10 <= len(digits_only) <= 13:
            redactions.append("phone:****")
            cleaned = cleaned.replace(p, "[REDACTED_PHONE]")

    # 5. Scrub personal names (contextual, plus First Last when other PII is present)
    for match in NAME_CONTEXT_REGEX.finditer(cleaned):
        name = match.group(1).strip()
        if name and name.lower() not in GEO_AND_COMMON_PROPER:
            redactions.append("name:****")
            cleaned = cleaned.replace(name, "[REDACTED_NAME]", 1)

    other_pii = any(r.startswith(("email:", "phone:", "aadhaar:", "ssn:", "card:")) for r in redactions)
    if other_pii:
        for match in STANDALONE_NAME_REGEX.finditer(cleaned):
            name = match.group(1).strip()
            if "[REDACTED" in name:
                continue
            if name.lower() in GEO_AND_COMMON_PROPER:
                continue
            redactions.append("name:****")
            cleaned = cleaned.replace(name, "[REDACTED_NAME]", 1)

    # Normalize whitespaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned, redactions


# ==============================================================================
# 2. SSRF PROTECTION ENGINE
# ==============================================================================
BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "metadata.google.internal",
    "instance-data",
}

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local / Cloud Metadata (AWS, Azure, GCP)
    ipaddress.ip_network("100.64.0.0/10"),    # Carrier-grade NAT
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
]


def validate_url_ssrf(url: str) -> Tuple[bool, str]:
    """
    Validate that a URL is safe to fetch and not attempting an SSRF attack.
    - Blocks non-HTTP(S) schemes (file://, ftp://, gopher://, dict://).
    - Resolves hostnames to verify that NO resolved IP is private, loopback, or cloud metadata.
    Returns: (is_safe, reason)
    """
    if not url or not isinstance(url, str):
        return False, "Empty or non-string URL."

    try:
        parsed = urlparse(url.strip())
    except Exception as e:
        return False, f"Malformed URL: {e}"

    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https"):
        return False, f"Blocked URL scheme: '{scheme}'. Only HTTP and HTTPS are permitted."

    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        return False, "Missing or invalid hostname in URL."

    if hostname in BLOCKED_HOSTNAMES:
        return False, f"Access to localhost/internal hostname '{hostname}' is blocked."

    # Direct IP literal check
    try:
        ip = ipaddress.ip_address(hostname)
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                return False, f"Access to private/internal IP address '{hostname}' is blocked."
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False, f"Access to restricted IP address '{hostname}' is blocked."
    except ValueError:
        pass  # It is a domain name, proceed to DNS resolution

    # Resolve domain to all IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        # If domain cannot be resolved, block it safely
        return False, f"Could not resolve hostname '{hostname}'."
    except Exception as e:
        return False, f"DNS resolution error for '{hostname}': {e}"

    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
            for net in BLOCKED_IP_NETWORKS:
                if ip in net:
                    return False, f"Hostname '{hostname}' resolves to restricted IP '{ip_str}'."
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False, f"Hostname '{hostname}' resolves to restricted IP '{ip_str}'."
        except ValueError:
            return False, f"Invalid resolved IP '{ip_str}'."

    return True, "Safe"


# ==============================================================================
# 3. RATE LIMITING & TAVILY BUDGET MANAGER
# ==============================================================================
class RateLimiter:
    """Sliding-window in-memory rate limiter."""

    def __init__(self, user_limit_per_min: int = 10, global_limit_per_min: int = 60):
        self.user_limit = user_limit_per_min
        self.global_limit = global_limit_per_min
        self._user_windows: Dict[str, List[float]] = {}
        self._global_window: List[float] = []

    def check_limit(self, user_id: str = "default_user") -> Tuple[bool, str]:
        """Check if request conforms to rate limits. Returns (allowed, error_msg)."""
        now = time.time()
        one_min_ago = now - 60.0

        # Global window prune
        self._global_window = [t for t in self._global_window if t > one_min_ago]
        if len(self._global_window) >= self.global_limit:
            return False, f"Global rate limit of {self.global_limit} requests/min exceeded. Please slow down."

        # User window prune
        u_times = [t for t in self._user_windows.get(user_id, []) if t > one_min_ago]
        if len(u_times) >= self.user_limit:
            return False, f"User rate limit of {self.user_limit} requests/min exceeded for '{user_id}'."

        # Record hit
        self._global_window.append(now)
        u_times.append(now)
        self._user_windows[user_id] = u_times
        return True, "OK"


class TavilyBudgetManager:
    """
    Tracks monthly Tavily API search usage against the free tier budget of 1,000 searches.
    Alerts at 80% (800 searches) and blocks when budget is exhausted.
    """

    def __init__(self, data_file: Optional[str] = None, monthly_cap: int = 1000, alert_threshold: int = 800):
        if data_file is None:
            data_file = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "data", "tavily_budget.json")
            )
        self.data_file = data_file
        self.monthly_cap = monthly_cap
        self.alert_threshold = alert_threshold
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            current_month = time.strftime("%Y-%m")
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump({current_month: 0}, f)

    def _get_current_month(self) -> str:
        return time.strftime("%Y-%m")

    def get_usage(self) -> Dict[str, Any]:
        """Get current month search count, limit, remaining, and alert status."""
        month = self._get_current_month()
        count = 0
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                count = data.get(month, 0)
        except Exception:
            count = 0

        alert = count >= self.alert_threshold
        exhausted = count >= self.monthly_cap

        return {
            "month": month,
            "searches_used": count,
            "monthly_cap": self.monthly_cap,
            "searches_remaining": max(0, self.monthly_cap - count),
            "alert_threshold": self.alert_threshold,
            "alert_triggered": alert,
            "exhausted": exhausted
        }

    def can_search(self) -> Tuple[bool, str]:
        """Check if quota remains for search."""
        usage = self.get_usage()
        if usage["exhausted"]:
            return False, f"Monthly Tavily search budget ({self.monthly_cap} requests) exhausted for {usage['month']}."
        if usage["alert_triggered"]:
            logger.warning(
                f"[TAVILY_BUDGET_ALERT] Used {usage['searches_used']}/{self.monthly_cap} searches for {usage['month']}! Approaching limit."
            )
        return True, "OK"

    def record_search(self) -> Dict[str, Any]:
        """Increment count by 1 and persist."""
        month = self._get_current_month()
        data = {}
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

        count = data.get(month, 0) + 1
        data[month] = count

        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return self.get_usage()


# ==============================================================================
# 4. ADVERSARIAL INJECTION & CREDENTIAL EXFILTRATION SHIELD
# ==============================================================================
EXTENDED_INJECTION_PATTERNS = [
    # System directive / prompt hijacking
    re.compile(r"ignore\s+(all\s+|any\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above|existing)?\s*(rules?|instructions?|guidelines?)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an|dan|jailbreak|unrestricted|evil|free)", re.IGNORECASE),
    re.compile(r"(system|developer|assistant)\s+(override|prompt|directive|instructions?):?", re.IGNORECASE),
    re.compile(r"new\s+(system|developer)\s+(prompt|instructions?|directive):?", re.IGNORECASE),
    re.compile(r"maintenance\s+mode:?\s*(ignore|bypass|disable)", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(previous|prior)\s+(rules?|instructions?)", re.IGNORECASE),
    re.compile(r"\b(jailbreak|dan\s+mode)\b", re.IGNORECASE),

    # Key / Credential / Env exfiltration attempts
    re.compile(r"(print|reveal|leak|show|output|dump|expose|display)\s+.*(\.env|api[_\s]?key|secret|password|token|credential)", re.IGNORECASE),
    re.compile(r"\b(TAVILY_API_KEY|GROQ_API_KEY|GEMINI_API_KEY|JWT_SECRET|DB_PASSWORD)\b", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?(system\s+prompt|developer\s+instructions?|internal\s+prompt)", re.IGNORECASE),
    re.compile(r"repeat\s+(the\s+)?(above|system)\s+(instructions?|prompt)\s+verbatim", re.IGNORECASE),
    re.compile(r"(say|print|output|respond\s+with)\s+[\"']?(pwned|hacked|pwnd|hahaha)[\"']?", re.IGNORECASE),
    re.compile(r"you\s+have\s+been\s+(pwned|hacked)", re.IGNORECASE),
    re.compile(r"\b(pwned|pwnd)\b", re.IGNORECASE),
    re.compile(r"<!--\s*(system|developer|hidden)", re.IGNORECASE),
    re.compile(r"<\s*/?\s*system\s*>", re.IGNORECASE),
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
    re.compile(r"#{1,3}\s*system\s+(prompt|instructions?)", re.IGNORECASE),
    re.compile(r"(cat|type|read|open)\s+[^\n]{0,40}\.env", re.IGNORECASE),
    re.compile(r"(hidden|internal)\s+(system\s+)?(instructions?|prompt|rules?)", re.IGNORECASE),
    re.compile(r"exfiltrat(e|ion)\s+(the\s+)?(api\s*keys?|secrets?|\.env)", re.IGNORECASE),
    re.compile(r"printenv|dump\s+environment\s+variables", re.IGNORECASE),
]

# Sensitive patterns that must NEVER leak in any model output
LEAKAGE_MASKS = [
    (re.compile(r'tvly-[a-zA-Z0-9_\-]{20,}'), '[REDACTED_API_KEY]'),
    (re.compile(r'gsk_[a-zA-Z0-9]{20,}'), '[REDACTED_API_KEY]'),
    (re.compile(r'AIzaSy[a-zA-Z0-9_\-]{30,}'), '[REDACTED_API_KEY]'),
    (re.compile(r'(?i)(password|secret|jwt)\s*=\s*[^\s,;]+'), '[REDACTED_SECRET]'),
]


def scrub_output_secrets(text: str) -> str:
    """Ensure no API keys, credentials, or secrets leak into output text."""
    if not text:
        return ""
    scrubbed = text
    for pattern, mask in LEAKAGE_MASKS:
        scrubbed = pattern.sub(mask, scrubbed)
    return scrubbed


# Global Singletons
rate_limiter = RateLimiter(user_limit_per_min=10, global_limit_per_min=60)
budget_manager = TavilyBudgetManager()
