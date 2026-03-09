from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Meal:
    meal_id: int
    name: str
    price: float
    allergens: str = ""
    image_url: str = ""

    def formatted_price(self) -> str:
        return f"{self.price:0.2f}€".replace(".", ",")
