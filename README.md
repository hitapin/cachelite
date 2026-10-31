# CacheLite

[![Tests](https://github.com/hitapin/cachelite/actions/workflows/tests.yml/badge.svg)](https://github.com/hitapin/cachelite/actions/workflows/tests.yml)

CacheLite is a small, dependency-free Python library that provides a thread-safe in-memory cache with time-to-live (TTL) expiration and least-recently-used (LRU) eviction.

> **Project status:** Initial prototype (`0.1.0`). This repository is a starting point; production suitability, performance, and broader compatibility have not yet been independently established.

## Features

- Per-entry TTL, with an optional default lifetime.
- Thread-safe access using a re-entrant lock.
- Optional maximum size with LRU eviction.
- Explicit cleanup of expired entries.
- No runtime third-party dependencies.

## Requirements

Python 3.10 or newer.

## Installation

```bash
python -m pip install .
```

For development and tests:

```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
```

## Quick start

```python
from cachelite import TTLCache

# Entries live for 60 seconds by default; keep at most 500 entries.
cache = TTLCache[str, dict](default_ttl=60, maxsize=500)

cache.set("profile:42", {"name": "Sam"})
profile = cache.get("profile:42")

# Override the TTL for an individual entry.
cache.set("temporary-token", "abc123", ttl=5)

# Remove expired entries and inspect the number removed.
removed = cache.cleanup()

cache.delete("profile:42")
cache.clear()
```

## API

- `TTLCache(default_ttl=None, maxsize=None)` creates a cache.
- `set(key, value, ttl=None)` stores a value. A `None` TTL uses the configured default; if both are `None`, the entry does not expire.
- `get(key, default=None)` returns a valid value or the default.
- `contains(key)` checks whether a valid entry exists.
- `delete(key)` removes a key and returns whether it existed.
- `clear()` removes all entries.
- `cleanup()` removes expired entries and returns the number removed.
- `len(cache)` returns the number of valid entries.

A TTL of zero expires an entry immediately. Negative TTLs and `maxsize` values below one raise `ValueError`.

## Limitations

CacheLite is process-local and in-memory: data is lost when the process exits and is not shared between workers or machines. It is not a distributed cache or a persistent data store. Applications with strict memory, durability, or distributed-consistency requirements should use infrastructure designed for those needs.

## Contributing

Bug reports, tests, documentation improvements, and focused feature proposals are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

MIT. See [LICENSE](LICENSE).
