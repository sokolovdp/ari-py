from __future__ import annotations

from typing import Any


class EventUnsubscriber:
    def __init__(self, listeners: list[Any], callback_obj: tuple[Any, ...]) -> None:
        self._listeners = listeners
        self._callback_obj = callback_obj

    def close(self) -> None:
        if self._callback_obj in self._listeners:
            self._listeners.remove(self._callback_obj)
