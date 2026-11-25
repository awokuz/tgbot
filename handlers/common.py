"""/start, /cancel va ustozning ro'yxatdan o'tishi."""
import logging
from typing import Optional

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import keyboards as kb
import texts as T
from database import db
from states import Reg
from utils import esc

log = logging.getLogger(__name__)
router = Router(name="common")

MEMBERS = ("owner", "admin", "teacher")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, role: Optional[str]) -> None:
    await state.clear()
    if role is None:
        # Yangi odam: avval ism-familiyasini so'raymiz
        await state.set_state(Reg.name)
        await message.answer(T.WELCOME_NEW, reply_markup=ReplyKeyboardRemove())
    elif role == "pending":
        await message.answer(T.WAITING)
    elif role == "blocked":
        await message.answer(T.BLOCKED)
    else:
        name = esc(message.from_user.full_name)
        await message.answer(T.WELCOME_BACK.format(name=name), reply_markup=kb.main_menu(role))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, role: Optional[str]) -> None:
    await state.clear()
    if role in MEMBERS:
        await message.answer(T.CANCELLED, reply_markup=kb.main_menu(role))
    else:
        await message.answer(T.NOT_STARTED, reply_markup=ReplyKeyboardRemove())


@router.message(Reg.name, F.text, ~F.text.startswith("/"))
async def reg_name(message: Message, state: FSMContext, bot: Bot) -> None:
    name = " ".join(message.text.split())
    if not 3 <= len(name) <= 60:
        await message.answer(T.ASK_NAME_AGAIN)
        return

    user = message.from_user
    await db.upsert_pending(user.id, name, user.username)
    await state.clear()
    await message.answer(T.REQUEST_SENT.format(name=esc(name)))

    # Direktor va adminlarga "Qabul qilish / Rad etish" tugmalari bilan xabar boramiz
    username = f" · @{user.username}" if user.username else ""
    text = T.NEW_REQUEST.format(name=esc(name), uid=user.id, username=esc(username))
    for staff_id in await db.staff_ids():
        try:
            await bot.send_message(staff_id, text, reply_markup=kb.request_kb(user.id))
        except TelegramAPIError:
            # Admin botga hali /start bosmagan bo'lishi mumkin — bu xato emas
            log.warning("So'rovni %s ga yuborib bo'lmadi", staff_id)


@router.message(Reg.name)
async def reg_name_not_text(message: Message) -> None:
    await message.answer(T.ASK_NAME_AGAIN)
