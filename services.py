"""Telegramga xabar yuborish bilan bog'liq umumiy ishlar."""
import asyncio
import logging
from typing import Dict, Iterable, List

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

import texts as T
from database import db
from utils import esc, exam_title

log = logging.getLogger(__name__)


async def send_items(bot: Bot, chat_id: int, items: Iterable[Dict]) -> None:
    """Imtihon bo'laklarini (matn, rasm, fayl) ketma-ket yuboradi.

    parse_mode=None: savoldagi < > & belgilari Telegram formatlashiga xalaqit bermasin.
    """
    for item in items:
        try:
            if item["ctype"] == "text":
                await bot.send_message(chat_id, item["content"], parse_mode=None)
            elif item["ctype"] == "photo":
                await bot.send_photo(
                    chat_id, item["content"], caption=item["caption"] or None, parse_mode=None
                )
            else:
                await bot.send_document(
                    chat_id, item["content"], caption=item["caption"] or None, parse_mode=None
                )
        except TelegramAPIError:
            log.exception("Imtihon bo'lagini yuborib bo'lmadi (item id=%s)", item.get("id"))
            await bot.send_message(chat_id, T.FILE_FAILED)
        await asyncio.sleep(0.05)  # Telegram limitiga tushib qolmaslik uchun


async def notify_new_exam(bot: Bot, exam: Dict, exclude_id: int) -> None:
    """Yangi imtihon qo'shilganda barcha faol foydalanuvchilarga xabar beradi."""
    ids: List[int] = list(db.owner_ids)
    for uid in await db.approved_ids():
        if uid not in ids:
            ids.append(uid)

    query = f"{exam['grade']} {exam['subject_name'].lower()} {exam['kind'].lower()}"
    text = T.NEW_EXAM_NOTICE.format(title=esc(exam_title(exam)), query=esc(query))
    for uid in ids:
        if uid == exclude_id:
            continue
        try:
            await bot.send_message(uid, text)
        except TelegramAPIError:
            pass  # foydalanuvchi botni bloklagan bo'lishi mumkin — bu xato emas
        await asyncio.sleep(0.05)
