"""
OMEGA Realtime Retrieval & Synthesis Pipeline (Stage 5)
======================================================
Wires together:
1. Safety & Guardrails (PII scrubbing, SSRF checks, rate limits, budget manager)
2. High-speed TTL Cache (with strict staleness prevention on network downtime)
3. Specialized Data Tools (weather, mandi, forex, stocks, web search, URL fetching)
4. Grounded Answer Synthesis (strict grounding, visible citations, UTC timestamps)
5. Defense-in-depth secret scrubbing on all outputs.
"""

import os
import re
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

from omega.realtime.safety import (
    scrub_pii,
    validate_url_ssrf,
    rate_limiter,
    budget_manager,
    scrub_output_secrets,
)
from omega.realtime.cache import cache
from omega.realtime.tools import (
    weather,
    mandi_prices,
    exchange_rate,
    stock_price,
    web_search,
    fetch_page,
)
from omega.realtime.generator import generator

logger = logging.getLogger("omega.realtime.pipeline")

# Standard downtime message for time-sensitive queries
NETWORK_DOWN_MSG = (
    "⚠️ Real-time network service is currently unavailable. "
    "Because this is a time-sensitive request, Omega will not serve stale or outdated information. "
    "Please check your network connection or try again shortly."
)

class RealtimePipeline:
    """
    End-to-end Realtime Information Pipeline for Omega.
    """

    def __init__(self, enable_cache: bool = True):
        self.enable_cache = enable_cache

    def classify_tool_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Heuristic sub-intent parser to identify the best specialized data tool
        before falling back to general Tavily web search.
        
        Returns: (tool_name, extracted_parameters)
        """
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # 1. Direct URL Detection
        url_match = re.search(r'https?://[^\s]+', q_clean)
        if url_match:
            return "fetch_page", {"url": url_match.group(0)}

        # 2. Weather Sub-intent
        # e.g., "weather in Delhi", "temperature in Mumbai", "delhi mausam", "is it raining in Bengaluru"
        weather_triggers = ["weather", "temperature", "forecast", "mausam", "rain", "barish", "humidity", "celsius"]
        if any(w in q_lower for w in weather_triggers):
            fillers = r'\b(what|is|the|how|current|today|right now|kaisa hai|kaisa|hoga|batao|kya hai|in|at|of|for|tell|me|show|weather|temperature|forecast|mausam|rain|barish)\b'
            loc = "New Delhi"
            m = re.search(r'\b(?:in|of|at|for)\s+([a-zA-Z\s]+)', q_clean, re.I)
            if m:
                cleaned = re.sub(fillers, '', m.group(1), flags=re.I).strip(' ?,.!')
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                if len(cleaned) >= 2:
                    loc = cleaned.title()
            else:
                cleaned = re.sub(fillers, '', q_clean, flags=re.I).strip(' ?,.!')
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                if len(cleaned) >= 2:
                    loc = cleaned.title()
            return "weather", {"location": loc}

        # 3. Forex / Currency Sub-intent
        # e.g., "USD to INR", "dollar to rupee", "eur to usd exchange rate", "forex rate"
        forex_triggers = ["usd to inr", "eur to usd", "gbp to inr", "dollar to inr", "exchange rate", "forex", "currency rate"]
        currency_codes = {
            "AED", "ARS", "AUD", "BDT", "BHD", "BRL", "CAD", "CHF", "CLP", "CNY",
            "COP", "CZK", "DKK", "EGP", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS",
            "INR", "JPY", "KES", "KRW", "KWD", "LKR", "MXN", "MYR", "NGN", "NOK",
            "NPR", "NZD", "OMR", "PEN", "PHP", "PKR", "PLN", "QAR", "RUB", "SAR",
            "SEK", "SGD", "THB", "TRY", "TWD", "USD", "VND", "ZAR"
        }
        currency_pair = re.search(r'\b([a-zA-Z]{3})\s*(?:to|in|\/)\s*([a-zA-Z]{3})\b', q_clean)
        is_currency_pair = currency_pair and all(code.upper() in currency_codes for code in currency_pair.groups())
        if any(ft in q_lower for ft in forex_triggers) or is_currency_pair:
            m = currency_pair if is_currency_pair else None
            if m:
                base = m.group(1).upper()
                target = m.group(2).upper()
            else:
                base = "USD"
                target = "INR"
            return "exchange_rate", {"base": base, "target": target}

        # 4. Stock Price Sub-intent
        # e.g., "stock price of TCS", "RELIANCE.NS share price", "AAPL ticker"
        stock_triggers = ["stock price", "share price", "stock quote", "ticker", "nasdaq", "nse", "bse"]
        if any(st in q_lower for st in stock_triggers) or ".ns" in q_lower or ".bo" in q_lower:
            fillers = r'\b(what|is|the|current|today|right now|kya hai|batao|in|of|at|for|tell|me|show|stock|price|share|ticker|quote|nasdaq|nse|bse)\b'
            cleaned = re.sub(fillers, '', q_clean, flags=re.I).strip(' ?,.!')
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            words = cleaned.split()
            candidate = words[0].upper() if words else "RELIANCE.NS"
            return "stock_price", {"symbol": candidate}

        # 5. Mandi / Agricultural Market Prices
        # e.g., "mandi price of onion in Maharashtra", "potato bhav in Agra mandi", "cotton rate in Gujarat"
        mandi_triggers = ["mandi", "bhav", "apmc", "crop price", "market price of", "wholesale price of"]
        if any(mt in q_lower for mt in mandi_triggers):
            common_commodities = [
                "onion", "potato", "tomato", "wheat", "rice", "cotton", "mustard",
                "soybean", "maize", "chickpea", "gram", "paddy", "garlic", "ginger",
                "pyaj", "aalu", "tamatar", "gehun", "dhan", "sarson", "kapas"
            ]
            found_commodity = "Onion"
            for c in common_commodities:
                if c in q_lower:
                    found_commodity = c.capitalize()
                    break
            
            states = [
                "Maharashtra", "Punjab", "Haryana", "Gujarat", "Madhya Pradesh",
                "Uttar Pradesh", "Rajasthan", "Karnataka", "Tamil Nadu", "Bihar",
                "Odisha", "Andhra Pradesh", "Telangana", "West Bengal"
            ]
            found_state = None
            for s in states:
                if s.lower() in q_lower:
                    found_state = s
                    break

            return "mandi_prices", {"commodity": found_commodity, "state": found_state}

        # 6. Default to General Real-time Web Search (news, cricket score, live events, facts)
        return "web_search", {"query": q_clean}

    def execute_tool(self, tool_name: str, params: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the designated data tool with caching, error catching, and network failure classification.
        """
        try:
            if tool_name == "weather":
                loc = params.get("location", "New Delhi")
                res = weather(loc)

            elif tool_name == "exchange_rate":
                base = params.get("base", "USD")
                target = params.get("target", "INR")
                res = exchange_rate(base, target)

            elif tool_name == "stock_price":
                symbol = params.get("symbol", "RELIANCE.NS")
                res = stock_price(symbol)

            elif tool_name == "mandi_prices":
                comm = params.get("commodity", "Onion")
                st = params.get("state")
                res = mandi_prices(comm, st)
                # If direct mandi API is blocked on key or returns no data, gracefully fallback to web_search
                if res.get("status") in ["blocked_missing_key", "error", "no_data"]:
                    search_q = f"current {comm} mandi price {st or ''} today India wholesale market"
                    res = web_search(search_q, user_id=user_id, apply_rate_limit=False)
                    res["tool"] = "web_search"

            elif tool_name == "fetch_page":
                url = params.get("url", "")
                res = fetch_page(url)

            elif tool_name == "web_search":
                q = params.get("query", "")
                res = web_search(q, user_id=user_id, apply_rate_limit=False)

            else:
                res = {"status": "error", "error": f"Unknown tool: {tool_name}"}

            return res

        except Exception as e:
            err_str = str(e).lower()
            if "connection" in err_str or "timeout" in err_str or "name resolution" in err_str:
                logger.error(f"Network error during tool execution {tool_name}: {e}")
                return {"status": "network_down", "error": str(e)}
            logger.error(f"Unexpected error executing {tool_name}: {e}")
            return {"status": "error", "error": str(e)}

    def run(
        self,
        query: str,
        user_id: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Full end-to-end execution of a realtime query through the safety, retrieval,
        and grounded answer generation pipeline.
        """
        pipeline_start = time.time()
        
        # 1. PII Scrubbing
        scrubbed_query, redacted_entities = scrub_pii(query)
        if redacted_entities:
            logger.info(f"Redacted PII from query ({len(redacted_entities)} items): {redacted_entities}")

        # 2. Per-User & Global Rate Limiting
        allowed, reason = rate_limiter.check_limit(user_id or "default_user")
        if not allowed:
            latency = round((time.time() - pipeline_start) * 1000, 2)
            return {
                "query": query,
                "scrubbed_query": scrubbed_query,
                "tool": "rate_limiter",
                "status": "blocked_rate_limit",
                "answer": f"⚠️ Rate limit exceeded: {reason}. Please wait a moment before sending another request.",
                "sources": [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "latency_ms": latency,
                "grounded": True
            }

        # 3. Sub-intent Identification
        tool_name, tool_params = self.classify_tool_intent(scrubbed_query)

        # 4. Check Cache
        cache_key = f"{tool_name}::{str(tool_params)}"
        cached_result = None
        if self.enable_cache and not force_refresh:
            cached_result = cache.get(cache_key, category="realtime")

        if cached_result:
            tool_result = cached_result
            from_cache = True
        else:
            # 5. Tool Execution
            tool_result = self.execute_tool(tool_name, tool_params, user_id=user_id)
            from_cache = False

            # Cache successful results
            if self.enable_cache and tool_result.get("status") == "success":
                cache.set(cache_key, tool_result, category="realtime", custom_ttl=600)

        # 6. Network Downtime & Fallback Handling
        # If internet/API is down: do NOT return stale data for time-sensitive queries
        if tool_result.get("status") in ["network_down", "connection_error"]:
            latency = round((time.time() - pipeline_start) * 1000, 2)
            return {
                "query": query,
                "scrubbed_query": scrubbed_query,
                "tool": tool_name,
                "status": "network_unavailable",
                "answer": NETWORK_DOWN_MSG,
                "sources": [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "latency_ms": latency,
                "grounded": True
            }

        actual_tool = tool_result.get("tool", tool_name)

        # 7. Grounded Answer Synthesis
        synthesis = generator.generate(
            query=scrubbed_query,
            tool_result=tool_result,
            tool_type=actual_tool
        )

        # 8. Secret Scrubbing on Output (Defense-in-depth)
        raw_answer = synthesis.get("answer", "")
        clean_answer = scrub_output_secrets(raw_answer)

        latency = round((time.time() - pipeline_start) * 1000, 2)

        return {
            "query": query,
            "scrubbed_query": scrubbed_query,
            "tool": actual_tool,
            "status": synthesis.get("status", "success"),
            "answer": clean_answer,
            "sources": synthesis.get("sources", []),
            "timestamp": synthesis.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())),
            "latency_ms": latency,
            "grounded": synthesis.get("grounded", True),
            "cached": from_cache
        }


# Singleton pipeline instance
pipeline = RealtimePipeline()

def run_realtime_pipeline(query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience functional interface."""
    return pipeline.run(query=query, user_id=user_id)
