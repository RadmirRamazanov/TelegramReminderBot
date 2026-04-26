from dataclasses import dataclass
from datetime import datetime


@dataclass
class Reminder:
    id: int | None
    user_id: int
    text: str
    remind_at: datetime
    is_sent: bool = False
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Текст напоминания не может быть пустым")
        if self.user_id <= 0:
            raise ValueError("user_id должен быть положительным числом")

    @property
    def remind_at_str(self) -> str:
        return self.remind_at.strftime("%d.%m.%Y %H:%M")

    @classmethod
    def from_row(cls, row: dict) -> "Reminder":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            text=row["text"],
            remind_at=datetime.fromisoformat(row["remind_at"]),
            is_sent=bool(row["is_sent"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
        )
