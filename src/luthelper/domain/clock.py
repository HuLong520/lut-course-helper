from __future__ import annotations

from datetime import datetime
from time import monotonic
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...

    def monotonic(self) -> float: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now()

    def monotonic(self) -> float:
        return monotonic()
