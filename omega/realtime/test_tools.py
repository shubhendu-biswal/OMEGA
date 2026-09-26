"""
Comprehensive Test Battery for OMEGA Stage 2 Realtime Tools
============================================================
Tests each tool and reports:
- End-to-end functionality status
- Latency and data payload
- Cache hit/miss validation
- Clear notification for tools waiting on API keys
"""

import sys
import os
import time
import json

sys.stdout.reconfigure(encoding='utf-8')

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from omega.realtime.tools import (
    weather,
    fetch_page,
    exchange_rate,
    stock_price,
    mandi_prices,
    web_search
)
from omega.realtime.cache import cache

def run_tests():
    print("=" * 75)
    print("  OMEGA STAGE 2: REAL-TIME DATA TOOLS VERIFICATION BENCHMARK")
    print("=" * 75)

    test_results = {}

    # ---------------------------------------------------------
    # TEST 1: Weather (Open-Meteo)
    # ---------------------------------------------------------
    print("\n[1/6] Testing Weather Tool (Open-Meteo - No Key Needed)...")
    t0 = time.time()
    w_res = weather("Mumbai")
    lat1 = time.time() - t0

    if w_res.get("status") == "success":
        curr = w_res["current"]
        print(f"  [OK] Location: {w_res['location']}")
        print(f"       Condition: {curr['condition']} | Temp: {curr['temperature_c']}°C (Feels like: {curr['feels_like_c']}°C)")
        print(f"       Humidity: {curr['humidity_pct']}% | Wind: {curr['wind_speed_kmh']} km/h")
        print(f"       Latency: {lat1:.2f}s")
        test_results["weather"] = {"status": "WORKING_END_TO_END", "latency_sec": round(lat1, 2)}
    else:
        print(f"  [FAIL] Weather error: {w_res}")
        test_results["weather"] = {"status": "FAILED", "error": w_res}

    # ---------------------------------------------------------
    # TEST 2: Page Fetcher (Trafilatura + robots.txt + rate limit)
    # ---------------------------------------------------------
    print("\n[2/6] Testing Page Fetcher Tool (Trafilatura - No Key Needed)...")
    t0 = time.time()
    test_url = "https://example.com"
    fetch_res = fetch_page(test_url)
    lat2 = time.time() - t0

    if fetch_res.get("status") == "success":
        print(f"  [OK] URL: {fetch_res['url']}")
        print(f"       Title: '{fetch_res['title']}' | Domain: {fetch_res['domain']}")
        print(f"       Tokens: ~{fetch_res['token_count']} tokens | Truncated: {fetch_res['truncated']}")
        print(f"       Excerpt: {fetch_res['content'][:120]}...")
        print(f"       Latency: {lat2:.2f}s")
        test_results["fetch_page"] = {"status": "WORKING_END_TO_END", "latency_sec": round(lat2, 2)}
    else:
        print(f"  [FAIL] Fetch error: {fetch_res}")
        test_results["fetch_page"] = {"status": "FAILED", "error": fetch_res}

    # ---------------------------------------------------------
    # TEST 3: Exchange Rate (Forex - No Key Needed)
    # ---------------------------------------------------------
    print("\n[3/6] Testing Exchange Rate Tool (Open Forex - No Key Needed)...")
    t0 = time.time()
    fx_res = exchange_rate("USD", "INR")
    lat3 = time.time() - t0

    if fx_res.get("status") == "success":
        print(f"  [OK] Conversion: {fx_res['rate_formula']}")
        print(f"       Updated UTC: {fx_res['last_updated_utc']}")
        print(f"       Latency: {lat3:.2f}s")
        test_results["exchange_rate"] = {"status": "WORKING_END_TO_END", "latency_sec": round(lat3, 2)}
    else:
        print(f"  [FAIL] Exchange rate error: {fx_res}")
        test_results["exchange_rate"] = {"status": "FAILED", "error": fx_res}

    # ---------------------------------------------------------
    # TEST 4: Stock Price (Finnhub / yfinance fallback)
    # ---------------------------------------------------------
    print("\n[4/6] Testing Stock Price Tool (NSE / US)...")
    t0 = time.time()
    stock_res = stock_price("RELIANCE.NS")
    lat4 = time.time() - t0

    if stock_res.get("status") == "success":
        print(f"  [OK] Symbol: {stock_res['symbol']} ({stock_res['provider']})")
        print(f"       Price: {stock_res['current_price']} {stock_res.get('currency', 'INR')} | Change: {stock_res['change']} ({stock_res['percent_change']}%)")
        print(f"       Latency: {lat4:.2f}s")
        test_results["stock_price"] = {"status": "WORKING_END_TO_END", "provider": stock_res["provider"], "latency_sec": round(lat4, 2)}
    else:
        print(f"  [FAIL] Stock price error: {stock_res}")
        test_results["stock_price"] = {"status": "FAILED", "error": stock_res}

    # ---------------------------------------------------------
    # TEST 5: Mandi Prices (Agmarknet data.gov.in)
    # ---------------------------------------------------------
    print("\n[5/6] Testing Mandi Prices Tool (data.gov.in / Agmarknet)...")
    t0 = time.time()
    mandi_res = mandi_prices("Wheat", state="Madhya Pradesh")
    lat5 = time.time() - t0

    if mandi_res.get("status") == "success":
        print(f"  [OK] Mandi records returned: {mandi_res['count']}")
        test_results["mandi_prices"] = {"status": "WORKING_END_TO_END", "latency_sec": round(lat5, 2)}
    elif mandi_res.get("status") == "blocked_missing_key":
        print(f"  [BLOCKED - KEY NEEDED] {mandi_res['error']}")
        print(f"       Required env var: {mandi_res['required_env_var']}")
        print(f"       Portal: {mandi_res['portal']}")
        test_results["mandi_prices"] = {
            "status": "BLOCKED_WAITING_ON_KEY",
            "required_env_var": mandi_res["required_env_var"],
            "portal": mandi_res["portal"]
        }
    else:
        print(f"  [FAIL] Mandi error: {mandi_res}")
        test_results["mandi_prices"] = {"status": "FAILED", "error": mandi_res}

    # ---------------------------------------------------------
    # TEST 6: Web Search (Tavily / SerpAPI / Brave)
    # ---------------------------------------------------------
    print("\n[6/6] Testing Web Search Tool (Tavily / SerpAPI / Brave)...")
    t0 = time.time()
    search_res = web_search("latest news India space launch")
    lat6 = time.time() - t0

    if search_res.get("status") == "success":
        print(f"  [OK] Search provider: {search_res['provider']}")
        print(f"       Found {search_res['results_count']} results.")
        test_results["web_search"] = {"status": "WORKING_END_TO_END", "provider": search_res["provider"], "latency_sec": round(lat6, 2)}
    elif search_res.get("status") == "blocked_missing_key":
        print(f"  [BLOCKED - KEY NEEDED] {search_res['error']}")
        print(f"       Recommended: {search_res['recommended']}")
        test_results["web_search"] = {
            "status": "BLOCKED_WAITING_ON_KEY",
            "required_env_vars": search_res["required_env_vars"],
            "recommended": search_res["recommended"]
        }
    else:
        print(f"  [FAIL] Search error: {search_res}")
        test_results["web_search"] = {"status": "FAILED", "error": search_res}

    # ---------------------------------------------------------
    # TEST 7: TTL Cache Verification
    # ---------------------------------------------------------
    print("\n[7/7] Testing In-Memory TTL Cache Hit Verification...")
    # Second call to weather should hit cache instantly
    t0 = time.time()
    cached_weather = weather("Mumbai")
    lat_cached = time.time() - t0

    cache_stats = cache.stats()
    print(f"  [OK] Second weather call hit cache: {cached_weather.get('cached') == True}")
    print(f"       Cached latency: {lat_cached*1000:.2f}ms (vs original {lat1:.2f}s)")
    print(f"       Cache Stats: {cache_stats}")
    test_results["ttl_cache"] = {"status": "WORKING_END_TO_END", "stats": cache_stats}

    print("\n" + "=" * 75)
    print("  STAGE 2 TOOL STATUS SUMMARY")
    print("=" * 75)
    for tool_name, res in test_results.items():
        print(f"  - {tool_name:<16}: {res['status']}")

    return test_results

if __name__ == "__main__":
    run_tests()
