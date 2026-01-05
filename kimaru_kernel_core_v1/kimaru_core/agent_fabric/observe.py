from __future__ import annotations
from typing import Callable, Dict, Any, List
import threading

class ObserveStream:
    def __init__(self):
        self._subs: List[Callable[[str, Dict[str, Any]], None]] = []
        self._lock = threading.Lock()

    def subscribe(self, fn: Callable[[str, Dict[str, Any]], None]) -> None:
        with self._lock:
            self._subs.append(fn)

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            subs = list(self._subs)
        for fn in subs:
            try:
                fn(event_type, payload)
            except Exception:
                # observation must never crash core
                pass
