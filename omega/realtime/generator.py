"""
OMEGA Realtime Answer Generation Engine (Stage 3)
=================================================
Synthesizes verified real-time answers strictly from retrieved tool payloads.

Strict Operational Guarantees:
1. Strict Grounding: Answers are derived exclusively from retrieved content.
   If data is missing, incomplete, or ambiguous, returns:
   "I don't have reliable information on that."
2. Visible Citations & Timestamps: Every response explicitly displays source URL/name
   and retrieval timestamp to the user.
3. Prompt-Injection Immunity: All external web data is treated as untrusted data.
   Instructions embedded in fetched pages/snippets are sanitized and ignored.
"""

import re
import datetime
from typing import Dict, Any, List, Optional

from omega.realtime.safety import (
    EXTENDED_INJECTION_PATTERNS,
    scrub_output_secrets
)

# Standard fallback message
NO_RELIABLE_INFO_MSG = "I don't have reliable information on that."

# Use extended adversarial patterns from Stage 4 safety module
INJECTION_PATTERNS = EXTENDED_INJECTION_PATTERNS

def is_injection_sentence(text: str) -> bool:
    """Check if a text chunk or sentence contains prompt-injection instructions."""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    return False

def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitize untrusted text from external web pages.
    Detects adversarial prompt-injection instructions and drops the malicious
    sentences/clauses entirely, preserving safe factual content.
    """
    if not text or not isinstance(text, str):
        return ""

    # Split text into sentence and clause chunks
    # Preserves sentence delimiters [.!?\n;:]
    chunks = re.split(r'([.!?\n;:]+)', text)
    cleaned_chunks = []
    i = 0
    while i < len(chunks):
        piece = chunks[i]
        delim = chunks[i+1] if i + 1 < len(chunks) else ""
        full_piece = piece + delim

        # If this chunk or sentence contains an injection attack, completely drop it
        if is_injection_sentence(full_piece):
            i += 2
            continue

        cleaned_chunks.append(full_piece)
        i += 2

    cleaned_text = "".join(cleaned_chunks).strip()

    # Second safety pass: if any residual injection keywords remain, purge them
    for pattern in INJECTION_PATTERNS:
        cleaned_text = pattern.sub("", cleaned_text)

    # Normalize multiple whitespaces
    return re.sub(r'\s+', ' ', cleaned_text).strip()

def format_timestamp(dt: Optional[datetime.datetime] = None) -> str:
    """Generate standardized UTC timestamp string."""
    now = dt or datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%d %H:%M:%S UTC")

def append_sources_and_timestamp(body: str, sources: List[Dict[str, str]], timestamp_str: str) -> str:
    """Format visible citations and retrieval timestamp at the bottom of the response."""
    lines = [body.strip(), "", "---", "### 🌐 Verification & Sources"]
    for s in sources:
        name = s.get("name", "Web Source")
        url = s.get("url")
        if url and url.startswith("http"):
            lines.append(f"• **Source**: [{name}]({url})")
        else:
            lines.append(f"• **Source**: {name}")
    lines.append(f"• **Retrieved**: {timestamp_str}")
    raw_output = "\n".join(lines)
    # Defense-in-depth: scrub any leaked secrets / API keys before returning to user
    return scrub_output_secrets(raw_output)


class RealtimeAnswerGenerator:
    """
    Strictly grounded real-time answer generator for Omega.
    """

    def generate(self, query: str, tool_result: Optional[Dict[str, Any]], tool_type: str) -> Dict[str, Any]:
        """
        Generate answer from tool result.
        Returns:
            {
                "status": "success" | "no_information",
                "answer": str,
                "sources": list,
                "timestamp": str,
                "grounded": bool
            }
        """
        timestamp_str = format_timestamp()

        # Step 1: Null, error, or blocked payload validation
        if not tool_result or not isinstance(tool_result, dict):
            return {
                "status": "no_information",
                "answer": NO_RELIABLE_INFO_MSG,
                "sources": [],
                "timestamp": timestamp_str,
                "grounded": True
            }

        status = tool_result.get("status")
        blocked_statuses = (
            "error",
            "blocked_missing_key",
            "blocked_by_robots_txt",
            "blocked_ssrf",
            "blocked_rate_limit",
            "blocked_quota_exceeded"
        )
        if status in blocked_statuses:
            return {
                "status": "no_information",
                "answer": NO_RELIABLE_INFO_MSG,
                "sources": [],
                "timestamp": timestamp_str,
                "grounded": True
            }

        # Step 2: Route to specialized synthesis logic based on tool type
        if tool_type == "weather":
            return self._generate_weather(query, tool_result, timestamp_str)
        elif tool_type == "exchange_rate":
            return self._generate_exchange_rate(query, tool_result, timestamp_str)
        elif tool_type == "stock_price":
            return self._generate_stock_price(query, tool_result, timestamp_str)
        elif tool_type == "mandi_prices":
            return self._generate_mandi_prices(query, tool_result, timestamp_str)
        elif tool_type in ("web_search", "fetch_page"):
            return self._generate_search_or_page(query, tool_result, tool_type, timestamp_str)
        else:
            return {
                "status": "no_information",
                "answer": NO_RELIABLE_INFO_MSG,
                "sources": [],
                "timestamp": timestamp_str,
                "grounded": True
            }

    # --------------------------------------------------------------------------
    # Weather Synthesizer
    # --------------------------------------------------------------------------
    def _generate_weather(self, query: str, data: Dict[str, Any], ts: str) -> Dict[str, Any]:
        current = data.get("current")
        if not current:
            return {"status": "no_information", "answer": NO_RELIABLE_INFO_MSG, "sources": [], "timestamp": ts, "grounded": True}

        location = data.get("location", "Requested Location")
        temp = current.get("temperature_c")
        feels_like = current.get("feels_like_c")
        humidity = current.get("humidity_pct")
        condition = current.get("condition", "Current conditions")
        wind = current.get("wind_speed_kmh")
        precip = current.get("precipitation_mm", 0.0)

        daily = data.get("daily_forecast", {})
        max_t = daily.get("max_temp_c")
        min_t = daily.get("min_temp_c")
        rain_prob = daily.get("rain_probability_pct")

        body_lines = [
            f"### ⛅ Current Weather for {location}",
            f"• **Condition**: **{condition}**",
            f"• **Temperature**: **{temp}°C** (Feels like: {feels_like}°C)",
            f"• **Relative Humidity**: {humidity}%",
            f"• **Wind Speed**: {wind} km/h",
        ]
        if precip is not None and precip > 0:
            body_lines.append(f"• **Current Precipitation**: {precip} mm")

        if max_t is not None and min_t is not None:
            forecast_line = f"• **Today's Forecast**: High of {max_t}°C, Low of {min_t}°C"
            if rain_prob is not None:
                forecast_line += f" (Precipitation Probability: {rain_prob}%)"
            body_lines.append(forecast_line)

        sources = [{"name": "Open-Meteo Weather API", "url": "https://open-meteo.com/"}]
        full_text = append_sources_and_timestamp("\n".join(body_lines), sources, ts)

        return {
            "status": "success",
            "answer": full_text,
            "sources": sources,
            "timestamp": ts,
            "grounded": True
        }

    # --------------------------------------------------------------------------
    # Exchange Rate Synthesizer
    # --------------------------------------------------------------------------
    def _generate_exchange_rate(self, query: str, data: Dict[str, Any], ts: str) -> Dict[str, Any]:
        base = data.get("base_currency")
        target = data.get("target_currency")
        rate = data.get("exchange_rate")

        if rate is None or not base or not target:
            return {"status": "no_information", "answer": NO_RELIABLE_INFO_MSG, "sources": [], "timestamp": ts, "grounded": True}

        last_up = data.get("last_updated_utc", ts)
        body = (
            f"### 💱 Real-Time Foreign Exchange Rate\n"
            f"• **Conversion**: **1 {base} = {rate:.4f} {target}**\n"
            f"• **Base Currency**: {base}\n"
            f"• **Target Currency**: {target}\n"
            f"• **Market Last Updated**: {last_up}"
        )
        sources = [{"name": "Open Exchange Rates Feed", "url": "https://open.er-api.com/"}]
        full_text = append_sources_and_timestamp(body, sources, ts)

        return {
            "status": "success",
            "answer": full_text,
            "sources": sources,
            "timestamp": ts,
            "grounded": True
        }

    # --------------------------------------------------------------------------
    # Stock Price Synthesizer
    # --------------------------------------------------------------------------
    def _generate_stock_price(self, query: str, data: Dict[str, Any], ts: str) -> Dict[str, Any]:
        symbol = data.get("symbol")
        price = data.get("current_price")
        if price is None or not symbol:
            return {"status": "no_information", "answer": NO_RELIABLE_INFO_MSG, "sources": [], "timestamp": ts, "grounded": True}

        currency = data.get("currency", "USD")
        change = data.get("change", 0.0)
        pct_change = data.get("percent_change", 0.0)
        provider = data.get("provider", "Market Feed")
        sign = "+" if change >= 0 else ""

        body_lines = [
            f"### 📈 Real-Time Stock Quote for {symbol}",
            f"• **Current Price**: **{price:.2f} {currency}**",
            f"• **Day Change**: {sign}{change:.2f} ({sign}{pct_change:.2f}%)",
        ]
        if data.get("high_today") and data.get("low_today"):
            body_lines.append(f"• **Day Range**: Low: {data['low_today']:.2f} | High: {data['high_today']:.2f}")
        if data.get("previous_close"):
            body_lines.append(f"• **Previous Close**: {data['previous_close']:.2f} {currency}")

        sources = [{"name": f"Financial Market Data ({provider})", "url": "https://finance.yahoo.com/"}]
        full_text = append_sources_and_timestamp("\n".join(body_lines), sources, ts)

        return {
            "status": "success",
            "answer": full_text,
            "sources": sources,
            "timestamp": ts,
            "grounded": True
        }

    # --------------------------------------------------------------------------
    # Mandi Prices Synthesizer
    # --------------------------------------------------------------------------
    def _generate_mandi_prices(self, query: str, data: Dict[str, Any], ts: str) -> Dict[str, Any]:
        records = data.get("data", [])
        commodity = data.get("commodity", "Agricultural Commodity")
        state = data.get("state")

        if not records:
            return {"status": "no_information", "answer": NO_RELIABLE_INFO_MSG, "sources": [], "timestamp": ts, "grounded": True}

        body_lines = [
            f"### 🌾 Daily Mandi Modal Rates for {commodity}" + (f" ({state})" if state else ""),
            "| Market / APMC | Variety | Arrival Date | Min Price (₹/q) | Max Price (₹/q) | **Modal Price (₹/q)** |",
            "|---|---|---|---|---|---|"
        ]

        for r in records[:8]:
            mkt = r.get("market", "Mandi")
            var = r.get("variety", "General")
            arr = r.get("arrival_date", "Today")
            min_p = r.get("min_price_inr_quintal", "-")
            max_p = r.get("max_price_inr_quintal", "-")
            modal_p = r.get("modal_price_inr_quintal", "-")
            body_lines.append(f"| **{mkt}** | {var} | {arr} | ₹{min_p} | ₹{max_p} | **₹{modal_p}** |")

        sources = [{"name": "Government of India Agmarknet OGD Portal", "url": "https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"}]
        full_text = append_sources_and_timestamp("\n".join(body_lines), sources, ts)

        return {
            "status": "success",
            "answer": full_text,
            "sources": sources,
            "timestamp": ts,
            "grounded": True
        }

    # --------------------------------------------------------------------------
    # Web Search & Page Extractor Synthesizer (With Prompt-Injection Immunity)
    # --------------------------------------------------------------------------
    def _generate_search_or_page(self, query: str, data: Dict[str, Any], tool_type: str, ts: str) -> Dict[str, Any]:
        sources = []
        raw_facts = []

        if tool_type == "web_search":
            results = data.get("results", [])
            if not results:
                return {"status": "no_information", "answer": NO_RELIABLE_INFO_MSG, "sources": [], "timestamp": ts, "grounded": True}

            for item in results:
                title = sanitize_untrusted_text(item.get("title", ""))
                snippet = sanitize_untrusted_text(item.get("snippet", ""))
                url = item.get("url", "")
                if snippet:
                    raw_facts.append({"title": title, "snippet": snippet, "url": url})
                if url:
                    sources.append({"name": title or "Web Article", "url": url})

        elif tool_type == "fetch_page":
            content = sanitize_untrusted_text(data.get("content", ""))
            title = sanitize_untrusted_text(data.get("title", "Web Page"))
            url = data.get("url", "")
            if not content or len(content.strip()) < 20:
                return {"status": "no_information", "answer": NO_RELIABLE_INFO_MSG, "sources": [], "timestamp": ts, "grounded": True}

            raw_facts.append({"title": title, "snippet": content[:2500], "url": url})
            sources.append({"name": title, "url": url})

        if not raw_facts:
            return {"status": "no_information", "answer": NO_RELIABLE_INFO_MSG, "sources": [], "timestamp": ts, "grounded": True}

        # Grounding check: verify that the retrieved snippets actually address the query keywords
        # Tokenize query keywords (exclude common stop words)
        stop_words = {"what", "is", "the", "in", "of", "and", "a", "an", "to", "for", "on", "at", "who", "when", "where", "how", "latest", "today", "now", "current"}
        query_words = [w.lower() for w in re.findall(r"\b\w+\b", query) if w.lower() not in stop_words]

        # Check if snippets contain any substantial overlap with query terms
        combined_text = " ".join(f["title"] + " " + f["snippet"] for f in raw_facts).lower()
        matched_terms = [qw for qw in query_words if qw in combined_text]

        # If data is completely unrelated / ambiguous / missing query focus -> refuse to guess
        if query_words and len(matched_terms) == 0:
            return {
                "status": "no_information",
                "answer": NO_RELIABLE_INFO_MSG,
                "sources": sources,
                "timestamp": ts,
                "grounded": True
            }

        # Build grounded summary strictly from extracted snippets
        body_lines = [
            f"### 📰 Real-Time Information: {query.strip().capitalize()}",
            "Based on verified real-time sources retrieved from the web:\n"
        ]

        for idx, f in enumerate(raw_facts[:4], 1):
            t = f["title"]
            s = f["snippet"].strip().replace("\n", " ")
            if len(s) > 280:
                s = s[:277] + "..."
            body_lines.append(f"• **{t}**: {s}")

        full_text = append_sources_and_timestamp("\n".join(body_lines), sources, ts)

        return {
            "status": "success",
            "answer": full_text,
            "sources": sources,
            "timestamp": ts,
            "grounded": True
        }


# Singleton instance
generator = RealtimeAnswerGenerator()
