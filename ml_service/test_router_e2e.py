import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTER_DIR = os.path.join(CURRENT_DIR, "assets", "v2", "intent")
if ROUTER_DIR not in sys.path:
    sys.path.insert(0, ROUTER_DIR)

from router import OmegaRouter

SAMPLE_QUERIES = [
    # 1-4: Math
    {"query": "What is 45 * 12?", "domain": "math"},
    {"query": "Solve the linear equation: 4x - 8 = 28", "domain": "math"},
    {"query": "Find the least common multiple (LCM) of 24 and 36", "domain": "math"},
    {"query": "500 rupaye ka 15 pratishat kitna hoga?", "domain": "math (hinglish)"},
    
    # 5-8: GK
    {"query": "Who was the first President of India?", "domain": "gk"},
    {"query": "Which body of water does the Godavari river flow into?", "domain": "gk"},
    {"query": "What is the capital of Australia?", "domain": "gk"},
    {"query": "ISRO ka mukhyalaya kis shahar mein sthit hai?", "domain": "gk (hinglish)"},
    
    # 9-11: Crop Recommendation
    {"query": "Which crop is best for Black soil with temperature 28 degrees?", "domain": "crop_recommendation"},
    {"query": "Suggest a suitable crop for Loamy soil at 18 degrees celsius", "domain": "crop_recommendation"},
    {"query": "Kali mitti me kharif season me konsi fasal lagana achha rahega?", "domain": "crop_recommendation (hinglish)"},
    
    # 12-14: Fertilizer Recommendation
    {"query": "What fertilizer should I apply for Wheat in Alluvial soil?", "domain": "fertilizer_recommendation"},
    {"query": "Which fertilizer is recommended for Rice in Clayey soil at 25 degrees?", "domain": "fertilizer_recommendation"},
    {"query": "Tamatar me nitrogen ki kami door karne ke liye konsi khad dale?", "domain": "fertilizer_recommendation (hinglish)"},
    
    # 15-17: Agriculture (Pest, Mandi, Irrigation)
    {"query": "How to control stem borer and yellow rust in wheat crops?", "domain": "agriculture"},
    {"query": "What is the wholesale mandi market price for mustard today?", "domain": "agriculture"},
    {"query": "Khet me drip sinchai aur sprinkler sinchai lagane ke kya fayde hain?", "domain": "agriculture (hinglish)"},
    
    # 18-19: Conversation
    {"query": "Hello Omega! What are your capabilities and how can you help me?", "domain": "conversation"},
    {"query": "Namaste bhai, kya haal chaal hai?", "domain": "conversation (hinglish)"},
    
    # 20: Out of Scope
    {"query": "Write a Python script to implement binary search algorithm", "domain": "out_of_scope"}
]

def run_e2e_tests():
    print("=" * 80)
    print("  OMEGA Stage 2: End-to-End Router Evaluation (20 Queries)")
    print("=" * 80)
    
    router = OmegaRouter(model_dir=ROUTER_DIR)
    results = []
    
    for idx, item in enumerate(SAMPLE_QUERIES, 1):
        q = item["query"]
        expected_cat = item["domain"]
        res = router.route(q)
        
        print(f"\n[{idx:02d}/20] Query: \"{q}\"")
        print(f"  Target Context: {expected_cat}")
        print(f"  Routed Intent:  {res['routed_intent'].upper()} (Confidence: {res['confidence'] * 100:.2f}%)")
        print(f"  Handler:        {res['handler']}")
        
        # Print snippet of response
        resp_lines = res["response"].strip().split("\n")
        snippet = "\n    ".join(resp_lines[:4])
        if len(resp_lines) > 4:
            snippet += "\n    ..."
        print(f"  Response Snippet:\n    {snippet}")
        
        results.append({
            "index": idx,
            "query": q,
            "expected_domain": expected_cat,
            "routed_intent": res["routed_intent"],
            "confidence": res["confidence"],
            "handler": res["handler"],
            "full_response": res["response"]
        })
        
    out_file = os.path.join(CURRENT_DIR, "data", "router_e2e_20_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved all 20 end-to-end execution logs to {out_file}")

if __name__ == "__main__":
    run_e2e_tests()
