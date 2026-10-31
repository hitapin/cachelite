"""A lightweight in-memory cache with per-entry time-to-live expiration."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Callable, Generic, TypeVar, cast

K = TypeVar("K")
V = TypeVar("V")
_MISSING = object()


@dataclass(frozen=True)
class _Entry(Generic[V]):
    value: V
    expires_at: float | None


class TTLCache(Generic[K, V]):
    """A small, thread-safe cache with optional TTL and LRU eviction.

    Args:
        default_ttl: Default lifetime in seconds. ``None`` means no expiry.
        maxsize: Maximum number of entries. Least-recently-used entries are
            evicted when this limit is exceeded. ``None`` means unlimited.

    A TTL of ``0`` expires an item immediately. Negative TTLs and max sizes
    below one are rejected.
    """

    def __init__(
        self,
        default_ttl: float | None = None,
        maxsize: int | None = None,
        *,
        _clock: Callable[[], float] = monotonic,
    ) -> None:
        if default_ttl is not None and default_ttl < 0:
            raise ValueError("default_ttl must be non-negative or None")
        if maxsize is not None and maxsize < 1:
            raise ValueError("maxsize must be at least 1 or None")

        self.default_ttl = default_ttl
        self.maxsize = maxsize
        self._clock = _clock
        self._items: OrderedDict[K, _Entry[V]] = OrderedDict()
        self._lock = RLock()

    def set(self, key: K, value: V, *, ttl: float | None = None) -> None:
        """Store ``value`` under ``key`` with an optional TTL override."""
        lifetime = self.default_ttl if ttl is None else ttl
        if lifetime is not None and lifetime < 0:
            raise ValueError("ttl must be non-negative or None")

        expires_at = None if lifetime is None else self._clock() + lifetime
        with self._lock:
            self._items[key] = _Entry(value=value, expires_at=expires_at)
            self._items.move_to_end(key)
            self._purge_expired_locked()
            if self.maxsize is not None:
                while len(self._items) > self.maxsize:
                    self._items.popitem(last=False)

    def get(self, key: K, default: V | None = None) -> V | None:
        """Return the cached value, or ``default`` when missing/expired."""
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return default
            if self._is_expired(entry):
                del self._items[key]
                return default
            self._items.move_to_end(key)
            return entry.value

    def contains(self, key: K) -> bool:
        """Return whether ``key`` has a non-expired entry."""
        marker = object()
        return self.get(key, cast(V, marker)) is not marker

    def delete(self, key: K) -> bool:
        """Delete ``key`` and return whether it existed."""
        with self._lock:
            return self._items.pop(key, _MISSING) is not _MISSING

    def clear(self) -> None:
        """Remove all cached entries."""
        with self._lock:
            self._items.clear()

    def cleanup(self) -> int:
        """Remove expired entries and return the number removed."""
        with self._lock:
            before = len(self._items)
            self._purge_expired_locked()
            return before - len(self._items)

    def __len__(self) -> int:
        """Return the number of currently valid entries."""
        with self._lock:
            self._purge_expired_locked()
            return len(self._items)

    def _is_expired(self, entry: _Entry[V]) -> bool:
        return entry.expires_at is not None and entry.expires_at <= self._clock()

    def _purge_expired_locked(self) -> None:
        expired = [key for key, entry in self._items.items() if self._is_expired(entry)]
        for key in expired:
            del self._items[key]
