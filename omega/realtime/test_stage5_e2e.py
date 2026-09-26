"""
OMEGA Stage 5: End-to-End Evaluation Battery (40 Queries + Downtime Fallback)
=============================================================================
Comprehensive test suite verifying:
- 20 Real-time queries (weather, mandi, forex, cricket, live news)
- 10 static general-knowledge queries
- 10 Out-of-scope queries (Coding, creative writing, recipes, DIY, travel)
- 1 Network downtime & fallback verification test
Logs latency, sources, timestamps, routing intent, and answers for manual review.
"""

import os
import sys
import time
import json
import importlib
from typing import Dict, Any, List
from unittest.mock import patch

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ROUTER_DIR = os.path.join(PROJECT_ROOT, "ml_service", "assets", "v2", "intent")
if ROUTER_DIR not in sys.path:
    sys.path.insert(0, ROUTER_DIR)

from router import OmegaRouter
from omega.realtime.pipeline import RealtimePipeline, pipeline

TEST_QUERIES = [
    # --- 1-20: Real-Time Queries ---
    # Weather (1-4)
    {"id": 1, "query": "What is the weather in Delhi right now?", "expected_intent": "realtime", "category": "weather"},
    {"id": 2, "query": "Current temperature and forecast in Mumbai", "expected_intent": "realtime", "category": "weather"},
    {"id": 3, "query": "London weather today", "expected_intent": "realtime", "category": "weather"},
    {"id": 4, "query": "How is the weather in Bengaluru?", "expected_intent": "realtime", "category": "weather"},
    
    # Mandi Prices (5-8)
    {"id": 5, "query": "Current mandi price of onion in Maharashtra", "expected_intent": "realtime", "category": "mandi"},
    {"id": 6, "query": "What is the price of wheat in Punjab mandi today?", "expected_intent": "realtime", "category": "mandi"},
    {"id": 7, "query": "Potato bhav in Agra mandi", "expected_intent": "realtime", "category": "mandi"},
    {"id": 8, "query": "Cotton rate in Gujarat APMC today", "expected_intent": "realtime", "category": "mandi"},
    
    # Forex / Currency (9-12)
    {"id": 9, "query": "USD to INR exchange rate today", "expected_intent": "realtime", "category": "forex"},
    {"id": 10, "query": "EUR to USD exchange rate", "expected_intent": "realtime", "category": "forex"},
    {"id": 11, "query": "GBP to INR currency rate", "expected_intent": "realtime", "category": "forex"},
    {"id": 12, "query": "JPY to USD exchange rate", "expected_intent": "realtime", "category": "forex"},
    
    # Cricket Scores (13-16)
    {"id": 13, "query": "Current India cricket score today", "expected_intent": "realtime", "category": "cricket"},
    {"id": 14, "query": "Live cricket score for today's India match", "expected_intent": "realtime", "category": "cricket"},
    {"id": 15, "query": "Latest cricket match score India today", "expected_intent": "realtime", "category": "cricket"},
    {"id": 16, "query": "India vs Australia live cricket score now", "expected_intent": "realtime", "category": "cricket"},
    
    # Live Events / Cricket / News (17-20)
    {"id": 17, "query": "Latest ISRO news today about space missions", "expected_intent": "realtime", "category": "news/space"},
    {"id": 18, "query": "Recent national news in India today", "expected_intent": "realtime", "category": "news/india"},
    {"id": 19, "query": "Current gold price in India today", "expected_intent": "realtime", "category": "news/market"},
    {"id": 20, "query": "Latest news about AI developments today", "expected_intent": "realtime", "category": "news/tech"},

    # --- 21-30: Static Domain Queries ---
    # GK (21-24)
    {"id": 21, "query": "Who was the first President of India?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 22, "query": "What is the capital of Australia?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 23, "query": "Which river is known as the Godavari?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 24, "query": "When did India gain independence?", "expected_intent": "gk", "category": "static_gk"},
    
    {"id": 25, "query": "Which is the highest mountain in the world?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 26, "query": "Where is the headquarters of ISRO?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 27, "query": "Who chaired the drafting committee of the Indian Constitution?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 28, "query": "Which planet is the largest in our solar system?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 29, "query": "What is the chemical formula for water?", "expected_intent": "gk", "category": "static_gk"},
    {"id": 30, "query": "In which city is the Taj Mahal located?", "expected_intent": "gk", "category": "static_gk"},

    # --- 31-40: Out-of-Scope Queries ---
    {"id": 31, "query": "Write a Python script to sort a list using quicksort", "expected_intent": "out_of_scope", "category": "coding"},
    {"id": 32, "query": "Write a poem about the autumn leaves", "expected_intent": "out_of_scope", "category": "creative"},
    {"id": 33, "query": "How do I fix a leaky faucet in my bathroom?", "expected_intent": "out_of_scope", "category": "diy"},
    {"id": 34, "query": "Write a cover letter for a software engineer job", "expected_intent": "out_of_scope", "category": "writing"},
    {"id": 35, "query": "What is the recipe for chocolate chip cookies?", "expected_intent": "out_of_scope", "category": "recipe"},
    {"id": 36, "query": "Write an essay about artificial intelligence in education", "expected_intent": "out_of_scope", "category": "essay"},
    {"id": 37, "query": "Write a story about a space pirate", "expected_intent": "out_of_scope", "category": "creative"},
    {"id": 38, "query": "How do I create a React web component with state?", "expected_intent": "out_of_scope", "category": "coding"},
    {"id": 39, "query": "Explain the rules of chess for castling in detail", "expected_intent": "out_of_scope", "category": "games"},
    {"id": 40, "query": "Write an itinerary for 3 days in Paris with budget tips", "expected_intent": "out_of_scope", "category": "travel"},
]

def run_offline_checks():
    """Validate routing and failure branches without making external requests."""
    router = OmegaRouter(model_dir=ROUTER_DIR)
    original_run = pipeline.run
    intent_parser_passes = (
        pipeline.classify_tool_intent("USD to INR exchange rate")[0] == "exchange_rate"
        and pipeline.classify_tool_intent("Live cricket score for today's India match")[0] == "web_search"
    )

    def stub_run(query, user_id=None, force_refresh=False):
        return {
            "answer": "Stubbed grounded response with a citation.",
            "tool": "web_search",
            "sources": [{"name": "Test source", "url": "https://example.com/"}],
            "timestamp": "2026-09-26 00:00:00 UTC",
            "latency_ms": 1,
            "status": "success",
        }

    try:
        pipeline.run = stub_run
        route_passes = 0
        realtime_dispatches = 0
        for item in TEST_QUERIES:
            result = router.route(item["query"], context={"user_id": f"offline_{item['id']}"})
            if result["routed_intent"] == item["expected_intent"]:
                route_passes += 1
            if item["expected_intent"] == "realtime" and result["handler"] == "OmegaRealtimePipeline":
                details = result.get("details", {})
                if details.get("sources") and details.get("timestamp"):
                    realtime_dispatches += 1
    finally:
        pipeline.run = original_run

    realtime_module = importlib.import_module("omega.realtime.pipeline")
    with patch.object(realtime_module, "mandi_prices", return_value={"status": "blocked_missing_key", "results": []}), \
         patch.object(realtime_module, "web_search", return_value={"status": "success", "tool": "web_search", "results": [{"title": "Mandi result"}]}):
        mandi = pipeline.execute_tool("mandi_prices", {"commodity": "Onion", "state": "Maharashtra"})
    mandi_fallback_ok = mandi.get("tool") == "web_search" and mandi.get("status") == "success"

    outage_pipeline = RealtimePipeline(enable_cache=False)
    outage_pipeline.execute_tool = lambda tool_name, params, user_id=None: {"status": "network_down", "error": "simulated outage"}
    outage = outage_pipeline.run("What is the weather in Delhi right now?", user_id="isolated_offline_outage", force_refresh=True)
    outage_ok = outage.get("status") == "network_unavailable" and "will not serve stale" in outage.get("answer", "")

    print(f"40-query expected intent routes: {route_passes}/40")
    print(f"Realtime sub-intent parser regression cases: {'PASS' if intent_parser_passes else 'FAIL'}")
    print(f"Realtime route dispatch with source and timestamp: {realtime_dispatches}/20")
    print(f"Mandi missing-key fallback to web_search: {'PASS' if mandi_fallback_ok else 'FAIL'}")
    print(f"Simulated network outage fallback: {'PASS' if outage_ok else 'FAIL'}")
    return route_passes == 40 and intent_parser_passes and realtime_dispatches == 20 and mandi_fallback_ok and outage_ok


def run_benchmark():
    print("=" * 80)
    print("  OMEGA Stage 5: End-to-End Evaluation Battery (40 Queries)")
    print("=" * 80)
    
    router = OmegaRouter(model_dir=ROUTER_DIR)
    print(f"Router loaded classes: {router.classes}\n")
    
    results = []
    correct_routes = 0
    total_latency_ms = 0.0
    
    for item in TEST_QUERIES:
        q_id = item["id"]
        q = item["query"]
        exp_intent = item["expected_intent"]
        cat = item["category"]
        
        # Isolate rate-limiting by assigning unique user_id per query
        user_ctx = {"user_id": f"benchmark_user_{q_id}"}
        
        t0 = time.time()
        res = router.route(q, context=user_ctx)
        duration_ms = round((time.time() - t0) * 1000, 2)
        total_latency_ms += duration_ms
        
        routed_intent = res["routed_intent"]
        is_route_correct = (routed_intent == exp_intent)
        if is_route_correct:
            correct_routes += 1
            
        details = res.get("details", {})
        sources = details.get("sources", [])
        timestamp = details.get("timestamp")
        tool_used = details.get("tool", res.get("handler", "N/A"))
        
        # Check answer validity
        resp_text = res.get("response", "")
        has_content = len(resp_text.strip()) > 20
        is_answer_valid = has_content and not ("error" in res.get("status", "").lower())
        
        status_sym = "[PASS]" if (is_route_correct and is_answer_valid) else "[FAIL]"
        
        print(f"[{q_id:02d}/40] {status_sym} Query: \"{q}\"")
        print(f"       Category: {cat} | Exp: {exp_intent} | Routed: {routed_intent} ({res['confidence']*100:.1f}%)")
        print(f"       Handler: {res['handler']} | Tool: {tool_used} | Latency: {duration_ms} ms")
        if sources:
            source_names = [s.get('name', 'Source') for s in sources[:2]]
            print(f"       Sources ({len(sources)}): {', '.join(source_names)}")
        if exp_intent == "realtime":
            print(f"       Timestamp included: {'yes' if timestamp else 'no'}")
        print(f"       Answer Snippet: {resp_text.strip().replace(chr(10), ' ')[:100]}...\n")
        
        results.append({
            "id": q_id,
            "query": q,
            "category": cat,
            "expected_intent": exp_intent,
            "routed_intent": routed_intent,
            "confidence": res["confidence"],
            "route_correct": is_route_correct,
            "handler": res["handler"],
            "tool": tool_used,
            "sources_count": len(sources),
            "sources": sources,
            "timestamp": timestamp,
            "timestamp_included": bool(timestamp),
            "latency_ms": duration_ms,
            "answer_valid": is_answer_valid,
            "answer_snippet": resp_text.strip()[:200],
            "answer_full": resp_text,
            "manual_correctness": "pending_manual_review"
        })
        
    avg_latency = round(total_latency_ms / len(TEST_QUERIES), 2)
    accuracy = round((correct_routes / len(TEST_QUERIES)) * 100, 2)
    realtime_results = [r for r in results if r["expected_intent"] == "realtime"]
    realtime_with_sources = sum(1 for r in realtime_results if r["sources_count"] > 0)
    realtime_with_timestamp = sum(1 for r in realtime_results if r["timestamp_included"])
    
    print("=" * 80)
    print(f"  BENCHMARK SUMMARY")
    print(f"  Routing Accuracy: {correct_routes}/{len(TEST_QUERIES)} ({accuracy}%)")
    print(f"  Average Query Latency: {avg_latency} ms")
    print(f"  Realtime responses with sources: {realtime_with_sources}/{len(realtime_results)}")
    print(f"  Realtime responses with timestamp: {realtime_with_timestamp}/{len(realtime_results)}")
    print("=" * 80)

    # --- Downtime Fallback Test ---
    print("\n>>> Testing Network Downtime Fallback Requirement...")
    original_execute = pipeline.execute_tool
    try:
        pipeline.execute_tool = lambda tool_name, params, user_id=None: {"status": "network_down", "error": "Connection drop"}
        down_res = pipeline.run("What is the weather in Delhi right now?", user_id="isolated_downtime_test_user", force_refresh=True)
        print(f"Downtime Test Status: {down_res['status']}")
        print(f"Downtime Response: {down_res['answer']}")
        downtime_passed = (
            down_res["status"] == "network_unavailable" and
            "Real-time network service is currently unavailable" in down_res["answer"] and
            "stale" in down_res["answer"]
        )
        print(f"Downtime Requirement Verified: {'PASS' if downtime_passed else 'FAIL'}")
    finally:
        pipeline.execute_tool = original_execute

    # Save benchmark results to JSON
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "stage5_benchmark_40_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_queries": len(TEST_QUERIES),
            "correct_routes": correct_routes,
            "accuracy_pct": accuracy,
            "avg_latency_ms": avg_latency,
            "realtime_with_sources": realtime_with_sources,
            "realtime_with_timestamp": realtime_with_timestamp,
            "downtime_fallback_verified": downtime_passed,
            "results": results
        }, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved full results to {out_file}")
    return accuracy, downtime_passed

if __name__ == "__main__":
    if "--offline" in sys.argv:
        if not run_offline_checks():
            raise SystemExit(1)
    else:
        run_benchmark()
