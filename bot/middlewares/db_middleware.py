import logging
from pathlib import Path
from typing import Any, Awaitable, Callable

import aiosqlite
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Открывает соединение с БД перед каждым хендлером и передаёт его через data["db"]."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            await conn.execute("PRAGMA foreign_keys = ON")
            data["db"] = conn
            return await handler(event, data)
