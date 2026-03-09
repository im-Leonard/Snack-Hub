from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from .meal import Meal


@dataclass(slots=True)
class Poll:
    poll_id: int
    start_date: date
    end_date: date
    is_active: bool = True
    meals: list[Meal] = field(default_factory=list)

    def publish(self) -> None:
        self.is_active = True

    def close(self) -> None:
        self.is_active = False

    def is_active(self):
        return self.end_date is None or datetime.now() < self.end_date


@dataclass(slots=True)
class Vote:
    vote_id: int
    timestamp: datetime
    meal: Meal
