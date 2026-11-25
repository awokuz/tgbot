"""Eng oxirgi router: ruxsati yo'qlar va eskirgan tugmalar uchun."""
from typing import Optional

from aiogram import Router
from aiogram.types import CallbackQuery, Message

import texts as T
from filters import HasRole

router = Router(name="gate")

NO_ACCESS = (None, "pending", "blocked")


@router.message(HasRole(*NO_ACCESS))
async def gate_message(message: Message, role: Optional[str]) -> None:
    text = {None: T.NOT_STARTED, "pending": T.WAITING, "blocked": T.BLOCKED}[role]
    await message.answer(text)


@router.callback_query(HasRole(*NO_ACCESS))
async def gate_callback(cb: CallbackQuery) -> None:
    await cb.answer(T.NO_ACCESS, show_alert=True)


@router.callback_query()
async def stale_callback(cb: CallbackQuery) -> None:
    """Hech bir handler olmagan tugma — odatda eski xabardagi eskirgan tugma."""
    await cb.answer(T.STALE_BUTTON, show_alert=True)
