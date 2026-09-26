"""
OMEGA Realtime Data Retrieval Tools (Stage 2)
=============================================
Provides production-grade tools for real-time web retrieval:
1. web_search(query): Tavily / SerpAPI / Brave search with structured output.
2. fetch_page(url): Trafilatura article extraction, 3,000 token cap, robots.txt, domain rate limiter.
3. weather(location): Open-Meteo geocoding and forecast (zero-key).
4. mandi_prices(commodity, state): Agmarknet data.gov.in integration with key check.
5. exchange_rate(base, target): Real-time currency forex rates (zero-key).
6. stock_price(symbol): Live stock quotes via Finnhub / AlphaVantage / yfinance.
All integrated with in-memory TTL caching.
"""

import os
import sys
import time
import json
import logging
import urllib.robotparser
from urllib.parse import urlparse, urljoin
from typing import Dict, Any, List, Optional
import requests
import trafilatura
from bs4 import BeautifulSoup
import yfinance as yf

from omega.realtime.cache import cache
from omega.realtime.safety import (
    scrub_pii,
    validate_url_ssrf,
    rate_limiter,
    budget_manager
)

logger = logging.getLogger("omega.realtime.tools")
logging.basicConfig(level=logging.INFO)

# Load environment variables from backend/.env if available
DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))
if os.path.exists(DOTENV_PATH):
    with open(DOTENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Domain Rate Limiter State
_LAST_REQUEST_TIME: Dict[str, float] = {}
_ROBOTS_PARSER_CACHE: Dict[str, urllib.robotparser.RobotFileParser] = {}
_DEFAULT_REQUEST_GAP = 1.0  # seconds per domain

# Weather code interpretations (WMO Code standard)
WMO_WEATHER_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

# ==============================================================================
# TOOL 1: Web Search
# ==============================================================================
def web_search(query: str, max_results: int = 5, user_id: str = "default_user", apply_rate_limit: bool = True) -> Dict[str, Any]:
    """
    Search the web for real-time information.
    Uses Tavily Search API (primary) or SerpAPI/Brave Search if configured.
    Guarded with:
    - Rate limits (per-user & global).
    - PII scrubbing (phone numbers, emails, national IDs stripped before search).
    - Monthly budget tracking for Tavily (1,000 free searches limit).
    Returns: {status, query, provider, results: [{title, url, snippet, date}]}
    """
    # 1. Rate Limiting Check (pipeline may already have applied the same limiter)
    if apply_rate_limit:
        allowed, rate_err = rate_limiter.check_limit(user_id)
        if not allowed:
            return {
                "status": "blocked_rate_limit",
                "error": rate_err,
                "query": query,
                "results": []
            }

    # 2. PII Scrubbing
    sanitized_query, redactions = scrub_pii(query)
    if redactions:
        logger.info(f"Scrubbed PII from web_search query: {redactions}")

    cache_key = f"search::{sanitized_query.lower().strip()}::{max_results}"
    cached_val = cache.get(cache_key, category="search")
    if cached_val is not None:
        cached_val["cached"] = True
        return cached_val

    tavily_key = os.getenv("TAVILY_API_KEY")
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    brave_key = os.getenv("BRAVE_API_KEY")

    # 1. Tavily Search API (Primary)
    if tavily_key:
        can_call, budget_msg = budget_manager.can_search()
        if not can_call:
            return {
                "status": "blocked_quota_exceeded",
                "error": budget_msg,
                "query": sanitized_query,
                "results": []
            }
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": tavily_key,
                "query": sanitized_query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": False
            }
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                budget_manager.record_search()
                data = res.json()
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "date": item.get("published_date") or None
                    })
                response = {
                    "status": "success",
                    "provider": "tavily",
                    "query": sanitized_query,
                    "pii_redacted": bool(redactions),
                    "results_count": len(results),
                    "results": results
                }
                cache.set(cache_key, response, category="search")
                return response
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")

    # 2. SerpAPI
    if serpapi_key:
        try:
            res = requests.get(
                "https://serpapi.com/search",
                params={"q": sanitized_query, "api_key": serpapi_key, "num": max_results, "engine": "google"},
                timeout=8
            )
            if res.status_code == 200:
                data = res.json()
                results = []
                for item in data.get("organic_results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "date": item.get("date") or None
                    })
                response = {
                    "status": "success",
                    "provider": "serpapi",
                    "query": sanitized_query,
                    "pii_redacted": bool(redactions),
                    "results_count": len(results),
                    "results": results
                }
                cache.set(cache_key, response, category="search")
                return response
        except Exception as e:
            logger.warning(f"SerpAPI failed: {e}")

    # 3. Brave Search
    if brave_key:
        try:
            res = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": sanitized_query, "count": max_results},
                headers={"Accept": "application/json", "X-Subscription-Token": brave_key},
                timeout=8
            )
            if res.status_code == 200:
                data = res.json()
                results = []
                for item in data.get("web", {}).get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "date": item.get("page_age") or None
                    })
                response = {
                    "status": "success",
                    "provider": "brave",
                    "query": sanitized_query,
                    "pii_redacted": bool(redactions),
                    "results_count": len(results),
                    "results": results
                }
                cache.set(cache_key, response, category="search")
                return response
        except Exception as e:
            logger.warning(f"Brave search failed: {e}")

    # If no key is provided, return transparent blocked status with registration guidance
    return {
        "status": "blocked_missing_key",
        "error": "No search API key provided.",
        "required_env_vars": ["TAVILY_API_KEY", "SERPAPI_API_KEY", "BRAVE_API_KEY"],
        "recommended": "TAVILY_API_KEY (Free 1,000 requests/month at https://tavily.com)",
        "query": sanitized_query,
        "results": []
    }

# ==============================================================================
# TOOL 2: Page Fetcher
# ==============================================================================
def _check_robots_txt(url: str, user_agent: str = "OmegaRealtimeBot/1.0") -> bool:
    """Check whether robots.txt allows crawling the given URL."""
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        if base_url not in _ROBOTS_PARSER_CACHE:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            try:
                rp.read()
                _ROBOTS_PARSER_CACHE[base_url] = rp
            except Exception:
                # If robots.txt cannot be fetched or parsed, assume permitted
                return True
        return _ROBOTS_PARSER_CACHE[base_url].can_fetch(user_agent, url)
    except Exception:
        return True

def _rate_limit_domain(netloc: str, min_interval: float = _DEFAULT_REQUEST_GAP) -> None:
    """Polite per-domain rate limiting."""
    now = time.time()
    last = _LAST_REQUEST_TIME.get(netloc, 0.0)
    elapsed = now - last
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    _LAST_REQUEST_TIME[netloc] = time.time()

def fetch_page(url: str, max_tokens: int = 3000) -> Dict[str, Any]:
    """
    Extract main article text only from URL.
    - Uses trafilatura for high-quality main content extraction (strips ads, nav, footer).
    - Respects robots.txt.
    - Enforces per-domain rate limiting.
    - Caps text at ~3,000 tokens (approx 12,000 characters).
    """
    cache_key = f"fetch::{url.strip()}"
    cached_val = cache.get(cache_key, category="news")
    if cached_val is not None:
        cached_val["cached"] = True
        return cached_val

    # 1. SSRF Protection FIRST (internal IPs, loopback, link-local, non-http schemes)
    is_safe, ssrf_err = validate_url_ssrf(url)
    if not is_safe:
        logger.warning(f"Blocked SSRF request to '{url}': {ssrf_err}")
        return {
            "status": "blocked_ssrf",
            "url": url,
            "error": f"SSRF Protection: {ssrf_err}"
        }

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {"status": "error", "error": f"Invalid URL: {url}", "url": url}

    # 2. Robots.txt Check
    if not _check_robots_txt(url):
        return {
            "status": "blocked_by_robots_txt",
            "url": url,
            "error": "Access prohibited by site robots.txt policy."
        }

    # 3. Rate Limiting
    _rate_limit_domain(parsed.netloc)

    # 4. HTTP Fetch & Article Extraction (no open redirect-to-private-IP)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        current_url = url
        res = None
        for _ in range(4):
            hop_safe, hop_err = validate_url_ssrf(current_url)
            if not hop_safe:
                logger.warning(f"Blocked SSRF redirect to '{current_url}': {hop_err}")
                return {
                    "status": "blocked_ssrf",
                    "url": url,
                    "error": f"SSRF Protection: {hop_err}"
                }
            res = requests.get(current_url, headers=headers, timeout=10, allow_redirects=False)
            if res.is_redirect or res.status_code in (301, 302, 303, 307, 308):
                loc = res.headers.get("Location")
                if not loc:
                    break
                current_url = urljoin(current_url, loc)
                continue
            break
        if res is None:
            return {"status": "error", "error": "Empty HTTP response", "url": url}
        if res.status_code != 200:
            return {
                "status": "error",
                "status_code": res.status_code,
                "error": f"HTTP {res.status_code} received from server",
                "url": url
            }

        html = res.text

        # Extract main text using trafilatura
        extracted_text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False
        )

        # Fallback to BeautifulSoup if trafilatura extracts nothing
        title = ""
        if not extracted_text:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()
            extracted_text = " ".join(soup.stripped_strings)
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
        else:
            soup = BeautifulSoup(html[:4000], "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Approximate token cap: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        truncated = False
        if len(extracted_text) > max_chars:
            extracted_text = extracted_text[:max_chars]
            truncated = True

        approx_tokens = len(extracted_text) // 4

        response = {
            "status": "success",
            "url": url,
            "title": title,
            "domain": parsed.netloc,
            "token_count": approx_tokens,
            "truncated": truncated,
            "content": extracted_text
        }
        cache.set(cache_key, response, category="news")
        return response

    except Exception as e:
        return {"status": "error", "error": str(e), "url": url}

# ==============================================================================
# TOOL 3: Weather (Open-Meteo)
# ==============================================================================
def weather(location: str) -> Dict[str, Any]:
    """
    Get live weather and short-term forecast for any city or district globally.
    Powered by Open-Meteo (zero API key required).
    """
    cache_key = f"weather::{location.strip().lower()}"
    cached_val = cache.get(cache_key, category="weather")
    if cached_val is not None:
        cached_val["cached"] = True
        return cached_val

    try:
        # Step 1: Geocode location to lat/lon
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": location, "count": 1, "language": "en", "format": "json"}
        geo_res = requests.get(geo_url, params=geo_params, timeout=6)
        if geo_res.status_code != 200:
            return {"status": "error", "error": "Geocoding service unavailable", "location": location}

        geo_data = geo_res.json()
        results = geo_data.get("results")
        if not results:
            return {"status": "error", "error": f"Location '{location}' not found", "location": location}

        loc_info = results[0]
        lat = loc_info["latitude"]
        lon = loc_info["longitude"]
        city = loc_info.get("name", location)
        admin1 = loc_info.get("admin1", "")
        country = loc_info.get("country", "")

        # Step 2: Fetch current weather + daily forecast
        forecast_url = "https://api.open-meteo.com/v1/forecast"
        forecast_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto"
        }
        f_res = requests.get(forecast_url, params=forecast_params, timeout=6)
        if f_res.status_code != 200:
            return {"status": "error", "error": "Weather forecast service unavailable", "location": location}

        f_data = f_res.json()
        current = f_data.get("current", {})
        daily = f_data.get("daily", {})

        w_code = current.get("weather_code", 0)
        condition = WMO_WEATHER_MAP.get(w_code, "Partly Cloudy")

        response = {
            "status": "success",
            "location": f"{city}, {admin1}, {country}".strip(", "),
            "coordinates": {"latitude": lat, "longitude": lon},
            "timestamp": current.get("time"),
            "current": {
                "temperature_c": current.get("temperature_2m"),
                "feels_like_c": current.get("apparent_temperature"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "condition": condition,
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "wind_direction_deg": current.get("wind_direction_10m"),
                "precipitation_mm": current.get("precipitation"),
                "surface_pressure_hpa": current.get("surface_pressure")
            },
            "daily_forecast": {
                "max_temp_c": daily.get("temperature_2m_max", [None])[0],
                "min_temp_c": daily.get("temperature_2m_min", [None])[0],
                "rain_probability_pct": daily.get("precipitation_probability_max", [None])[0]
            }
        }
        cache.set(cache_key, response, category="weather")
        return response

    except Exception as e:
        return {"status": "error", "error": str(e), "location": location}

# ==============================================================================
# TOOL 4: Mandi Prices (data.gov.in / Agmarknet)
# ==============================================================================
def mandi_prices(commodity: str, state: Optional[str] = None, market: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch live APMC mandi prices for agricultural commodities.
    Endpoint: data.gov.in official Agmarknet resource.
    - Requires DATA_GOV_IN_API_KEY environment variable.
    - Returns structured modal, min, and max rates per quintal.
    """
    cache_key = f"mandi::{commodity.lower().strip()}::{str(state).lower()}::{str(market).lower()}"
    cached_val = cache.get(cache_key, category="prices")
    if cached_val is not None:
        cached_val["cached"] = True
        return cached_val

    api_key = os.getenv("DATA_GOV_IN_API_KEY")
    if not api_key:
        return {
            "status": "blocked_missing_key",
            "error": "DATA_GOV_IN_API_KEY is required to access official government Agmarknet mandi APIs.",
            "required_env_var": "DATA_GOV_IN_API_KEY",
            "portal": "https://data.gov.in/",
            "registration_steps": [
                "1. Visit https://data.gov.in/ and register/login with mobile/email.",
                "2. Go to 'My Account' -> 'API Key Management'.",
                "3. Generate your instant, free API key.",
                "4. Add to your .env file: DATA_GOV_IN_API_KEY=your_key_here"
            ],
            "commodity": commodity,
            "state": state
        }

    try:
        resource_id = "9ef84268-d588-465a-a308-a864a43d0070"  # Agmarknet daily price resource
        url = f"https://api.data.gov.in/resource/{resource_id}"
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": 25,
            "filters[commodity]": commodity.capitalize()
        }
        if state:
            params["filters[state]"] = state.capitalize()
        if market:
            params["filters[market]"] = market.capitalize()

        res = requests.get(url, params=params, timeout=8)
        if res.status_code == 200:
            data = res.json()
            records = data.get("records", [])
            parsed_records = []
            for r in records:
                parsed_records.append({
                    "state": r.get("state"),
                    "district": r.get("district"),
                    "market": r.get("market"),
                    "commodity": r.get("commodity"),
                    "variety": r.get("variety"),
                    "arrival_date": r.get("arrival_date"),
                    "min_price_inr_quintal": r.get("min_price"),
                    "max_price_inr_quintal": r.get("max_price"),
                    "modal_price_inr_quintal": r.get("modal_price")
                })

            response = {
                "status": "success",
                "provider": "data.gov.in (Agmarknet)",
                "commodity": commodity,
                "state": state,
                "count": len(parsed_records),
                "data": parsed_records
            }
            cache.set(cache_key, response, category="prices")
            return response
        else:
            return {
                "status": "error",
                "status_code": res.status_code,
                "error": f"data.gov.in returned HTTP {res.status_code}: {res.text[:200]}"
            }

    except Exception as e:
        return {"status": "error", "error": str(e), "commodity": commodity}

# ==============================================================================
# TOOL 5: Exchange Rates (Forex)
# ==============================================================================
def exchange_rate(base: str = "USD", target: str = "INR") -> Dict[str, Any]:
    """
    Fetch real-time currency exchange rates.
    Powered by open ExchangeRate-API (zero API key required).
    """
    base = base.upper().strip()
    target = target.upper().strip()

    cache_key = f"forex::{base}::{target}"
    cached_val = cache.get(cache_key, category="prices")
    if cached_val is not None:
        cached_val["cached"] = True
        return cached_val

    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            rates = data.get("rates", {})
            rate = rates.get(target)
            if rate is None:
                return {
                    "status": "error",
                    "error": f"Target currency '{target}' not supported",
                    "base": base,
                    "target": target
                }

            response = {
                "status": "success",
                "base_currency": base,
                "target_currency": target,
                "exchange_rate": rate,
                "rate_formula": f"1 {base} = {rate:.4f} {target}",
                "last_updated_utc": data.get("time_last_update_utc"),
                "next_update_utc": data.get("time_next_update_utc")
            }
            cache.set(cache_key, response, category="prices")
            return response
        else:
            return {"status": "error", "error": f"Forex service returned HTTP {res.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e), "base": base, "target": target}

# ==============================================================================
# TOOL 6: Stock & Commodity Prices
# ==============================================================================
def stock_price(symbol: str) -> Dict[str, Any]:
    """
    Fetch real-time stock prices and financial metrics.
    Supports Indian NSE/BSE stocks (e.g. RELIANCE.NS, TCS.NS, ^NSEI, ^BSESN)
    and Global stocks (e.g. AAPL, TSLA, NVDA).
    Uses Finnhub if FINNHUB_API_KEY is set, with seamless yfinance zero-key fallback.
    """
    symbol = symbol.upper().strip()
    cache_key = f"stock::{symbol}"
    cached_val = cache.get(cache_key, category="prices")
    if cached_val is not None:
        cached_val["cached"] = True
        return cached_val

    finnhub_key = os.getenv("FINNHUB_API_KEY")

    # 1. Finnhub API (if key available)
    if finnhub_key:
        try:
            url = "https://finnhub.io/api/v1/quote"
            res = requests.get(url, params={"symbol": symbol, "token": finnhub_key}, timeout=6)
            if res.status_code == 200:
                data = res.json()
                if data.get("c") and data["c"] != 0:
                    response = {
                        "status": "success",
                        "provider": "finnhub",
                        "symbol": symbol,
                        "current_price": data.get("c"),
                        "change": data.get("d"),
                        "percent_change": data.get("dp"),
                        "high_today": data.get("h"),
                        "low_today": data.get("l"),
                        "open_today": data.get("o"),
                        "previous_close": data.get("pc")
                    }
                    cache.set(cache_key, response, category="prices")
                    return response
        except Exception as e:
            logger.warning(f"Finnhub failed: {e}")

    # 2. Resilient Zero-Key Fallback: Yahoo Finance (via yfinance)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        last_price = info.last_price
        prev_close = info.previous_close

        if last_price is not None:
            change = last_price - prev_close if prev_close else 0.0
            pct_change = (change / prev_close * 100.0) if prev_close else 0.0

            response = {
                "status": "success",
                "provider": "yfinance (zero-key)",
                "symbol": symbol,
                "current_price": round(float(last_price), 2),
                "currency": getattr(info, "currency", "INR" if ".NS" in symbol or ".BO" in symbol else "USD"),
                "change": round(float(change), 2),
                "percent_change": round(float(pct_change), 2),
                "high_today": round(float(info.day_high), 2) if getattr(info, "day_high", None) else None,
                "low_today": round(float(info.day_low), 2) if getattr(info, "day_low", None) else None,
                "previous_close": round(float(prev_close), 2) if prev_close else None
            }
            cache.set(cache_key, response, category="prices")
            return response
        else:
            return {"status": "error", "error": f"Symbol '{symbol}' not found or inactive."}

    except Exception as e:
        return {"status": "error", "error": str(e), "symbol": symbol}
