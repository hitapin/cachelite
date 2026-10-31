import unittest

from cachelite import TTLCache


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TTLCacheTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.cache = TTLCache(default_ttl=10, _clock=self.clock)

    def test_set_and_get(self):
        self.cache.set("answer", 42)
        self.assertEqual(self.cache.get("answer"), 42)

    def test_missing_key_returns_default(self):
        self.assertEqual(self.cache.get("missing", "fallback"), "fallback")

    def test_entry_expires(self):
        self.cache.set("short", "lived", ttl=2)
        self.clock.advance(2)
        self.assertIsNone(self.cache.get("short"))

    def test_ttl_can_be_overridden(self):
        self.cache.set("long", "lived", ttl=30)
        self.clock.advance(11)
        self.assertEqual(self.cache.get("long"), "lived")

    def test_cleanup_returns_removed_count(self):
        self.cache.set("one", 1, ttl=1)
        self.cache.set("two", 2, ttl=5)
        self.clock.advance(2)
        self.assertEqual(self.cache.cleanup(), 1)
        self.assertEqual(len(self.cache), 1)

    def test_lru_eviction(self):
        cache = TTLCache(maxsize=2, _clock=self.clock)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.get("a")  # a becomes most recently used
        cache.set("c", 3)
        self.assertTrue(cache.contains("a"))
        self.assertFalse(cache.contains("b"))
        self.assertTrue(cache.contains("c"))

    def test_delete_and_clear(self):
        self.cache.set("a", 1)
        self.assertTrue(self.cache.delete("a"))
        self.assertFalse(self.cache.delete("a"))
        self.cache.set("b", 2)
        self.cache.clear()
        self.assertEqual(len(self.cache), 0)

    def test_invalid_ttl_is_rejected(self):
        with self.assertRaises(ValueError):
            self.cache.set("bad", "value", ttl=-1)

    def test_invalid_maxsize_is_rejected(self):
        with self.assertRaises(ValueError):
            TTLCache(maxsize=0)


if __name__ == "__main__":
    unittest.main()
