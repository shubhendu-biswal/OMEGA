# OMEGA Realtime Web Retrieval & Synthesis Engine

Production-grade real-time web retrieval, grounded answer generation, and multi-tier security pipeline for OMEGA.

---

## 🚀 Architecture Overview

The system consists of five fully integrated layers:

```
User Query
   │
   ▼
[ Safety & Guardrails ] ─────────► PII Redaction (Phone, Email, Aadhaar, SSN)
   │                             ► Rate Limiter (Per-user & Global)
   │                             ► Tavily Budget Tracker (1,000/mo cap)
   ▼
[ Intent Router v2 ]  ───────────► 8-Class Intent Classifier (realtime, math, gk, agri, etc.)
   │ (if realtime)
   ▼
[ Sub-Intent Dispatcher ] ───────► Tool Selection (Weather, Mandi, Forex, Stock, Web, URL)
   │
   ▼
[ High-Speed TTL Cache ] ────────► Multi-tier caching with strict downtime staleness prevention
   │
   ▼
[ Specialized Data Tools ] ──────► Open-Meteo (Zero-Key Weather)
   │                             ► Open Forex API (Zero-Key Exchange Rates)
   │                             ► yfinance (Zero-Key Stock Quotes)
   │                             ► Agmarknet / data.gov.in (Mandi Prices)
   │                             ► Tavily Search API (Real-Time Web Search)
   │                             ► Trafilatura (Article Extraction + SSRF Shield)
   ▼
[ Grounded Answer Generator ] ───► Strict grounding (Zero parametric hallucinations)
   │                             ► Visible citations & UTC timestamps
   │                             ► Adversarial Prompt Injection Defense
   ▼
[ Secret Scrubbing Layer ] ──────► Defense-in-depth API key redaction (`tvly-*`, `gsk_*`, `AIza*`)
   │
   ▼
Final Grounded Response
```

---

## 🛠️ Key Capabilities & Features

1. **Zero-Key Out-of-the-Box Operation**:
   - **Weather**: Real-time current temperature, humidity, wind, and forecast via Open-Meteo.
   - **Forex**: Instant real-time conversion rates across 160+ fiat currencies via Open Exchange Rates.
   - **Stock Quotes**: Live prices, day ranges, and percentage changes via Yahoo Finance.
   - **Page Extraction**: Trafilatura web scraper with SSRF protection and robots.txt compliance.

2. **Web Search & Mandi Market Intelligence**:
   - Integrated Tavily live search with automatic modal price extraction for Indian Mandis.
   - Graceful fallback: If direct Agmarknet key is unconfigured, automatically retrieves verified mandi rates via search.

3. **Production Security Guardrails**:
   - **PII Scrubbing**: Prevents user emails, Indian phone numbers, Aadhaar, and SSNs from reaching external APIs.
   - **SSRF Defense**: Rejects loopback (`127.0.0.1`), private RFC 1918 subnets (`10.x`, `172.16.x`, `192.168.x`), cloud metadata endpoints (`169.254.169.254`), and non-HTTP(S) schemes.
   - **Prompt Injection Defense**: Sanitizes untrusted web snippets against jailbreak attempts and instructions like `"ignore previous instructions"`.
   - **Secret Scrubbing**: Guarantees no internal API keys or credentials leak into user responses.

4. **Time-Sensitive Downtime Protection**:
   - If the network or an external API is down, the engine explicitly notifies the user rather than serving stale cache data for time-sensitive queries.

---

## 📦 Setup & Installation

### 1. Install Dependencies
```bash
pip install -r omega/realtime/requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `backend/.env` and supply your API keys:
```bash
cp omega/realtime/.env.example backend/.env
```

Ensure `TAVILY_API_KEY` is set in `backend/.env`.

---

## 🧪 Testing

Run the test suites:
```bash
# Stage 2 Tools Test
python -m unittest omega/realtime/test_tools.py

# Stage 3 Answer Generator Test
python -m unittest omega/realtime/test_generator.py

# Stage 4 Safety & Guardrails Test
python -m unittest omega/realtime/test_safety.py

# Stage 5 End-to-End Pipeline & Router Test
python omega/realtime/test_stage5_e2e.py
```
