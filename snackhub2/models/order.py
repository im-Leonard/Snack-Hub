from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .meal import Meal


@dataclass(slots=True)
class OrderItem:
    meal: Meal
    quantity: int
    price_at_order: float

    def calculate_sub_total(self) -> float:
        return float(self.quantity) * float(self.price_at_order)


@dataclass(slots=True)
class Order:
    order_id: int
    order_date: date
    pickup_date: Optional[date] = None
    is_paid: bool = False
    items: list[OrderItem] = field(default_factory=list)

    def calculate_total(self) -> float:
        return sum(i.calculate_sub_total() for i in self.items)
