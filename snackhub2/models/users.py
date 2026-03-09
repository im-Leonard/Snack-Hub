from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(slots=True)
class User(ABC):
    user_id: int
    email: str
    password_hash: str
    is_active: bool = True

    def login(self) -> bool:
        return True

    def logout(self) -> None:
        return None

    @property
    def username(self) -> str:
        return self.email

    def to_page_data(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": getattr(self, "role", None),
        }


@dataclass(slots=True)
class Admin(User):
    role: str = "admin"

    def create_user(self, u: User) -> None:
        return None

    def delete_user(self, user_id: int) -> None:
        return None

    def reset_password(self, user_id: int) -> None:
        return None

    def block_user(self, user_id: int) -> None:
        return None


@dataclass(slots=True)
class Student(User):
    first_name: str = ""
    last_name: str = ""
    class_grade: str = ""
    balance: float = 0.0
    role: str = "schueler"

    def vote(self, poll: Any, meal: Any) -> None:
        return None

    def place_order(self, order: Any) -> None:
        return None


@dataclass(slots=True)
class CanteenStaff(User):
    role: str = "kantine"

    def create_poll(self) -> None:
        return None

    def manage_meals(self) -> None:
        return None

    def view_stats(self) -> None:
        return None


def user_from_db_row(row: dict[str, Any]) -> User:
    user_id = int(row.get("id") or row.get("user_id") or 0)
    username = str(row.get("username") or row.get("email") or "")
    password_hash = str(row.get("password_hash") or row.get("passwordHash") or "")
    role = str(row.get("role") or "")
    is_active = bool(row.get("is_active", True))

    if role == "schueler":
        return Student(user_id=user_id, email=username, password_hash=password_hash, is_active=is_active)
    if role == "kantine":
        return CanteenStaff(user_id=user_id, email=username, password_hash=password_hash, is_active=is_active)
    if role == "admin":
        return Admin(user_id=user_id, email=username, password_hash=password_hash, is_active=is_active)

    # Fallback: generischer User-Typ (Student ist am kompatibelsten mit bestehenden Rollen)
    return Student(user_id=user_id, email=username, password_hash=password_hash, is_active=is_active, role=role or "schueler")
