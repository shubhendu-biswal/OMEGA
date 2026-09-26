"""
OMEGA Realtime In-Memory Thread-Safe TTL Cache
==============================================
Provides high-speed caching for live real-time tools with domain-specific
Time-To-Live (TTL) policies:
- weather: 10 minutes (600s)
- prices (mandi, stock, forex): 15 minutes (900s)
- news / page extracts: 5 minutes (300s)
- search results: 30 minutes (1800s)
"""

import time
import threading
from typing import Any, Optional, Dict, Tuple, Callable
from functools import wraps

# Default TTL durations in seconds
DEFAULT_TTLS: Dict[str, int] = {
    "weather": 600,   # 10 minutes
    "prices": 900,    # 15 minutes (Mandi, Stocks, Forex)
    "news": 300,      # 5 minutes
    "search": 1800,   # 30 minutes
    "default": 600,   # 10 minutes fallback
}

class TTLCache:
    """Thread-safe in-memory cache with category-specific TTL expiration."""

    def __init__(self, ttls: Optional[Dict[str, int]] = None):
        self.ttls = dict(DEFAULT_TTLS)
        if ttls:
            self.ttls.update(ttls)
        self._cache: Dict[str, Tuple[Any, float, str]] = {}  # key -> (value, expiry_timestamp, category)
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def _get_ttl(self, category: str, custom_ttl: Optional[int] = None) -> int:
        if custom_ttl is not None and custom_ttl > 0:
            return custom_ttl
        return self.ttls.get(category.lower(), self.ttls["default"])

    def _normalize_key(self, key: Any, category: str) -> str:
        return f"{category.lower()}::{str(key).strip().lower()}"

    def get(self, key: Any, category: str = "default") -> Optional[Any]:
        """Retrieve a value if present and not expired."""
        norm_key = self._normalize_key(key, category)
        now = time.time()

        with self._lock:
            if norm_key in self._cache:
                val, expiry, _ = self._cache[norm_key]
                if now < expiry:
                    self._hits += 1
                    return val
                else:
                    # Expired
                    del self._cache[norm_key]
            self._misses += 1
            return None

    def set(self, key: Any, value: Any, category: str = "default", custom_ttl: Optional[int] = None) -> None:
        """Store a value with category TTL."""
        norm_key = self._normalize_key(key, category)
        ttl = self._get_ttl(category, custom_ttl)
        expiry = time.time() + ttl

        with self._lock:
            self._cache[norm_key] = (value, expiry, category)

    def has(self, key: Any, category: str = "default") -> bool:
        """Check if unexpired key exists without updating hit/miss counts."""
        norm_key = self._normalize_key(key, category)
        now = time.time()
        with self._lock:
            if norm_key in self._cache:
                _, expiry, _ = self._cache[norm_key]
                if now < expiry:
                    return True
                else:
                    del self._cache[norm_key]
            return False

    def invalidate(self, key: Any, category: str = "default") -> bool:
        """Remove a specific key."""
        norm_key = self._normalize_key(key, category)
        with self._lock:
            if norm_key in self._cache:
                del self._cache[norm_key]
                return True
            return False

    def clear(self, category: Optional[str] = None) -> int:
        """Clear all keys or all keys in a given category."""
        with self._lock:
            if category is None:
                count = len(self._cache)
                self._cache.clear()
                return count
            else:
                cat_lower = category.lower()
                to_del = [k for k, (_, _, cat) in self._cache.items() if cat == cat_lower]
                for k in to_del:
                    del self._cache[k]
                return len(to_del)

    def cleanup_expired(self) -> int:
        """Purge all expired entries."""
        now = time.time()
        with self._lock:
            expired = [k for k, (_, expiry, _) in self._cache.items() if now >= expiry]
            for k in expired:
                del self._cache[k]
            return len(expired)

    def stats(self) -> Dict[str, Any]:
        """Return cache health and usage statistics."""
        with self._lock:
            now = time.time()
            active_count = sum(1 for _, expiry, _ in self._cache.values() if now < expiry)
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100.0) if total_requests > 0 else 0.0
            return {
                "active_entries": active_count,
                "total_entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_pct": round(hit_rate, 2),
                "configured_ttls_sec": dict(self.ttls)
            }

# Global singleton instance
cache = TTLCache()

def cached(category: str, key_builder: Optional[Callable[..., str]] = None, custom_ttl: Optional[int] = None):
    """Decorator to cache function results automatically."""
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default composite key
                args_str = ",".join(str(a) for a in args)
                kwargs_str = ",".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{fn.__name__}({args_str};{kwargs_str})"

            cached_val = cache.get(cache_key, category=category)
            if cached_val is not None:
                return cached_val

            result = fn(*args, **kwargs)
            # Only cache non-error results if dict has status
            if isinstance(result, dict) and result.get("status") in ("error", "blocked_missing_key"):
                return result

            cache.set(cache_key, result, category=category, custom_ttl=custom_ttl)
            return result
        return wrapper
    return decorator
