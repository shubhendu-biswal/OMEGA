# OMEGA Realtime Pipeline Status

**Status snapshot:** 2026-09-27  
**Overall:** Integrated and guarded, but not production sign-off complete. Routing and safety checks pass; factual quality and intermittent provider availability remain open issues.

## Tool Status

| Tool | Status | Provider and key requirements |
|---|---|---|
| `weather` | Worked in the live Stage 5 run (4/4); the later smoke run timed out at Open-Meteo geocoding. Treat availability as intermittent. | Open-Meteo geocoding and forecast APIs; no API key. |
| `exchange_rate` | Worked in the live Stage 5 run (4/4); the later smoke run failed DNS resolution for the provider. Treat availability as intermittent. | ExchangeRate-API (`open.er-api.com`); no API key. |
| `stock_price` | Working in the latest smoke run via `yfinance` for `RELIANCE.NS`. | Finnhub is optional (`FINNHUB_API_KEY`); zero-key Yahoo Finance via `yfinance` is the fallback and worked. |
| `fetch_page` | Working in the latest smoke run for `https://example.com`; extraction returned the page title and body. | Trafilatura/HTTP; no API key. SSRF and robots.txt checks apply. |
| `web_search` | Working. Live Tavily search returned results; latest tool smoke returned five results. | Tavily primary (`TAVILY_API_KEY`). Optional fallbacks are SerpAPI (`SERPAPI_API_KEY`) and Brave (`BRAVE_API_KEY`). |
| `mandi_prices` | Direct official Agmarknet API is blocked until its key is set. Realtime pipeline fallback to Tavily `web_search` is implemented and passed a live Stage 5 run. Search prices can conflict or refer to a different market. | Official data.gov.in Agmarknet requires `DATA_GOV_IN_API_KEY`; it is currently absent. Search fallback uses `TAVILY_API_KEY`. |

Weather and exchange rates returned successfully during the live 40-query run, but their follow-up smoke tests encountered network timeout/DNS errors. This document records both observations rather than treating one successful run as guaranteed current uptime.

## API Keys And Configuration

Realtime environment configuration is read from `backend/.env`. That file is git-ignored. Do not copy secret values into documentation, logs, tests, or chat.

- `TAVILY_API_KEY`: required for the configured primary live web-search provider. Present; verified masked fingerprint `tvly-dev-3wDf...QJk`, different from the prior fingerprint. Plaintext intentionally omitted.
- `DATA_GOV_IN_API_KEY`: required for direct official Agmarknet mandi prices. Absent; mandi requests fall back to web search.
- `SERPAPI_API_KEY`: optional search fallback. Absent.
- `BRAVE_API_KEY`: optional search fallback expected by `tools.py`. Absent. Configuration-name mismatch: `.env.example` documents `BRAVE_SEARCH_API_KEY`, which the code does not read.
- `FINNHUB_API_KEY`: optional stock quote provider. Absent; zero-key `yfinance` fallback works.
- `ALPHA_VANTAGE_API_KEY`: listed in `.env.example`, but current `stock_price` implementation does not read or use it. It is not currently required or active.

Separate backend credentials such as `GEMINI_API_KEY` and `GROQ_API_KEY` are used by other application functions, not required by these realtime retrieval tools. Realtime response synthesis is performed by the local grounded generator.

### Secret Exposure Audit

- `TRAINING_LOG.md`: current scan found zero Tavily-key-shaped strings and zero credential-like assignments.
- Saved Copilot transcript for this session: scan found three Tavily-key-shaped matches. The key was present in the user's chat message. Therefore it is **not accurate to claim that the credential was never present in chat history**. The scan did not print or disclose matched text. Chat history was not modified.
- The configured `.env` value was checked only through a masked fingerprint in terminal output and this document. The live Tavily request returned results.

Because the credential was included in persisted chat history, rotate it if chat logs are within the organization's secret-exposure threat model. Continue to keep `.env` ignored and restrict access to local transcript storage.

## Safety Protections And Boundaries

`ChatController.java` sends detected realtime requests to Flask `/predict-realtime`; it does not independently implement these protections. The Python `omega.realtime.pipeline` is the enforcement point. Thus Java requests that reach this endpoint inherit these controls, but it would be inaccurate to say the Java controller itself duplicates or enforces each control.

| Protection | Python realtime pipeline | Java `ChatController` path |
|---|---|---|
| PII redaction | Active before classification/retrieval; search tool also scrubs queries. Covers configured patterns for emails, phone numbers, Aadhaar, SSN, cards, and contextual names. | Delegated: raw prompt is forwarded to `/predict-realtime`; Python scrubs it before external retrieval. No independent Java PII scrubber. |
| SSRF blocking | Active in `fetch_page`, including HTTP(S)-only validation, hostname/IP checks, DNS resolution, and redirect-hop validation. | Delegated when the request enters Python `fetch_page`; no independent Java SSRF validator. |
| Rate limits | Active in pipeline: 10 requests/user/minute and 60 globally/minute. Search assumes the pipeline already checked the limit. | Delegated through `/predict-realtime`; there is no equivalent Java rate limiter on this branch. |
| Tavily budget | Active for Tavily calls: monthly cap 1,000; blocked at the cap. Other search providers are not counted against the Tavily budget. | Delegated through the Python endpoint. |
| Prompt-injection sanitization | Active on untrusted retrieved text in the answer generator; secret output scrubber runs before returning. | Delegated through the Python endpoint; no separate Java web-result sanitizer is used in the current realtime path. |

The safety suite passed **45/45 tests** on 2026-09-27, including PII, SSRF, rate-limit, budget alert/exhaustion, injection, and key-scrubbing cases. The simulated network outage returned the explicit no-stale-data `network_unavailable` response.

## Tavily Usage

Persisted local budget file: `omega/realtime/data/tavily_budget.json`.

- Current month: **2026-09**
- Recorded local usage: **46 / 1,000**
- Alert threshold: **800 / 1,000 (80%)**
- Remaining local budget: **954**

This is the application's locally recorded successful Tavily-call count, not an authoritative account-side usage report. Cache hits and calls outside this application may make the provider's account dashboard differ.

## Validation And Known Limitations

- Offline 40-query expected intent routing: **40/40**. Currency-pair regression cases passed after restricting forex parsing to recognized currency codes.
- Live Stage 5 benchmark: **40/40 intended routes**, **1,549.53 ms** average query latency; all **20/20 realtime** responses included sources and timestamps. This is route accuracy, not answer correctness.
- Manual answer assessment of that live set: **25 correct, 4 partial, 11 incorrect**. All 10 out-of-scope refusals were appropriate. Static GK retrieval returned unrelated answers for 6/10 queries. Cricket search results were frequently rankings, stale scores, or unrelated matches; ISRO results included historical mission material rather than reliably current news. This blocks factual-quality sign-off.
- Mandi fallback was exercised in the live set, but search results sometimes conflicted on prices or locality. Official direct data remains unavailable until `DATA_GOV_IN_API_KEY` is configured.
- The latest all-tool smoke test passed fetch, stock, and Tavily; weather timed out, exchange-rate lookup failed DNS, and direct mandi reported the missing key. Earlier live 40-query results for weather and exchange rates succeeded. Provider/network availability is therefore intermittent.
- Scikit-learn runtime is pinned to **1.9.1** in `ml_service/requirements.txt`, matching the realtime intent artifact. The older GK TF-IDF artifacts still emit `InconsistentVersionWarning` for serialization under 1.8.0; they were not re-exported. Pinning 1.9.1 resolves the realtime router model mismatch but does not make every legacy artifact version-uniform.
- `BRAVE_SEARCH_API_KEY` in `.env.example` does not match the `BRAVE_API_KEY` name read by code. Alpha Vantage is documented but unused. Align or remove these entries before enabling those providers.
- Fetch-page robots.txt retrieval failure is permissive in the current implementation; this should be revisited if policy requires fail-closed behavior.
- In-memory rate-limit state and TTL cache do not coordinate across multiple worker processes. Tavily budget storage is a local JSON counter, not a distributed/transactional quota ledger.

## Remaining Work

1. Improve GK retrieval precision and enforce a similarity threshold so unrelated answers produce the reliable-information fallback.
2. Improve freshness/relevance validation for cricket and news searches; avoid presenting stale or mismatched scorecards as current.
3. Add locality/date consistency checks and prefer official mandi data once `DATA_GOV_IN_API_KEY` is available.
4. Resolve the remaining 1.8.0 GK-artifact serialization mismatch by regenerating compatible artifacts or isolating the old runtime.
5. Fix the Brave env-name mismatch and remove or implement the unused Alpha Vantage option.
6. Consider distributed rate/budget controls and stricter robots.txt failure behavior for multi-worker deployments.
7. Rotate Tavily again if persisted chat transcripts require credential-free history; the session transcript currently contains three key-shaped matches.
