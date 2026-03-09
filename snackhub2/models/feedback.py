from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .meal import Meal


@dataclass(slots=True)
class Feedback:
    feedback_id: int
    content: str
    rating_stars: int
    timestamp: datetime
    meal: Meal
