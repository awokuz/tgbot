"""Faqat bot egasi uchun: adminlarni qo'shish va olib tashlash."""
import logging
from typing import Union

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import texts as T
from database import db
from filters import HasRole
from keyboards import OwnerCb
from states import AddAdmin
from ui import respond
from utils import esc

log = logging.getLogger(__name__)
router = Router(name="owner")
router.message.filter(HasRole("owner"))
router.callback_query.filter(HasRole("owner"))


async def show_admins(target: Union[Message, CallbackQuery]) -> None:
    admins = await db.list_admins()
    if admins:
        lines = "\n".join(f"🛡 {esc(a['full_name'])} · <code>{a['user_id']}</code>" for a in admins)
    else:
        lines = T.ADMINS_NONE
    await respond(target, T.ADMINS_TITLE.format(lines=lines), kb.admins_kb(admins))


@router.callback_query(OwnerCb.filter(F.act == "list"))
async def admins_list(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await show_admins(cb)


@router.callback_query(OwnerCb.filter(F.act == "add"))
async def admin_add_ask(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddAdmin.user_id)
    await respond(cb, T.ADMIN_ASK_ID, kb.admins_back_kb())


@router.message(AddAdmin.user_id, F.text, ~F.text.startswith("/"))
async def admin_add_id(message: Message, state: FSMContext, bot: Bot) -> None:
    raw = message.text.strip()
    if not raw.isdigit():
        await message.answer(T.ADMIN_BAD_ID)
        return
    uid = int(raw)
    if db.is_owner(uid):
        await message.answer(T.ADMIN_IS_OWNER)
        return

    await db.make_admin(uid)
    await state.clear()
    await message.answer(T.ADMIN_ADDED.format(uid=uid))
    try:
        await bot.send_message(uid, T.ADMIN_ADDED_NOTICE)
    except TelegramAPIError:
        # Odam botga hali /start bosmagan — o'zi kirganda admin ekanini ko'radi
        log.info("Yangi adminga (%s) xabar yuborib bo'lmadi", uid)


@router.message(AddAdmin.user_id)
async def admin_add_not_text(message: Message) -> None:
    await message.answer(T.ADMIN_BAD_ID)


@router.callback_query(OwnerCb.filter(F.act == "rm"))
async def admin_remove_ask(cb: CallbackQuery, callback_data: OwnerCb) -> None:
    user = await db.get_user(callback_data.id)
    if user is None:
        await cb.answer(T.USER_NOT_FOUND, show_alert=True)
        return
    text = T.ADMIN_CONFIRM_REMOVE.format(name=esc(user["full_name"]))
    await respond(cb, text, kb.admin_confirm_remove_kb(user["user_id"]))


@router.callback_query(OwnerCb.filter(F.act == "rmyes"))
async def admin_remove_yes(cb: CallbackQuery, callback_data: OwnerCb, bot: Bot) -> None:
    user = await db.get_user(callback_data.id)
    if user is None:
        await cb.answer(T.USER_NOT_FOUND, show_alert=True)
        return
    await db.remove_admin(user["user_id"])
    try:
        await bot.send_message(user["user_id"], T.ADMIN_REMOVED_NOTICE)
    except TelegramAPIError:
        pass
    await show_admins(cb)
