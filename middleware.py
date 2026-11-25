"""Har bir xabar/tugma bosilganda foydalanuvchi rolini aniqlab, handlerlarga beradi."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database import db


class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Faqat shaxsiy chat: guruhlarda bot jim turadi (imtihonlar begonalarga ko'rinmasin)
        chat = getattr(event, "chat", None) or getattr(getattr(event, "message", None), "chat", None)
        if chat is not None and chat.type != "private":
            return None

        user = getattr(event, "from_user", None)
        role = None
        if user is not None and not user.is_bot:
            role = await db.get_role(user.id)
            if role in ("admin", "teacher", "pending", "blocked"):
                await db.touch_user(user.id, user.username, user.full_name)
        data["role"] = role
        return await handler(event, data)
