"""Pastki menyu tugmalari. Bu router eng birinchi turadi: menyu tugmasi bosilsa,
foydalanuvchi qaysi bosqichda bo'lishidan qat'i nazar, o'sha bosqich bekor qilinadi."""
from typing import Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import texts as T
from filters import HasRole
from handlers import admin, owner, teacher

router = Router(name="menu")

MEMBERS = ("owner", "admin", "teacher")
STAFF = ("owner", "admin")


@router.message(F.text == T.BTN_EXAMS, HasRole(*MEMBERS))
async def btn_exams(message: Message, state: FSMContext) -> None:
    await state.clear()
    await teacher.show_subjects(message)


@router.message(F.text == T.BTN_SEARCH, HasRole(*MEMBERS))
async def btn_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(T.SEARCH_HINT)


@router.message(F.text == T.BTN_HELP, HasRole(*MEMBERS))
async def btn_help(message: Message, state: FSMContext, role: Optional[str]) -> None:
    await state.clear()
    text = T.HELP_TEACHER
    if role in STAFF:
        text += T.HELP_STAFF_EXTRA
    if role == "owner":
        text += T.HELP_OWNER_EXTRA
    await message.answer(text)


@router.message(F.text == T.BTN_ADD_EXAM, HasRole(*STAFF))
async def btn_add_exam(message: Message, state: FSMContext) -> None:
    await admin.start_add_exam(message, state)


@router.message(F.text == T.BTN_ADD_SUBJECT, HasRole(*STAFF))
async def btn_add_subject(message: Message, state: FSMContext) -> None:
    await admin.start_add_subject(message, state)


@router.message(F.text == T.BTN_USERS, HasRole(*STAFF))
async def btn_users(message: Message, state: FSMContext) -> None:
    await state.clear()
    await admin.show_users(message)


@router.message(F.text == T.BTN_ADMINS, HasRole("owner"))
async def btn_admins(message: Message, state: FSMContext) -> None:
    await state.clear()
    await owner.show_admins(message)
