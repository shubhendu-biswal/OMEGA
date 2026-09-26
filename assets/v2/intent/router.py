import os
import sys

# Wrapper script pointing to ml_service/assets/v2/intent/router.py
TARGET_ROUTER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml_service", "assets", "v2", "intent"))
if TARGET_ROUTER_PATH not in sys.path:
    sys.path.insert(0, TARGET_ROUTER_PATH)

from router import OmegaRouter

if __name__ == "__main__":
    router = OmegaRouter(model_dir=TARGET_ROUTER_PATH)
    sample = "What is 25 + 75?"
    res = router.route(sample)
    print("Router initialized successfully:", res)
