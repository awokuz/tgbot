"""Imtihonlarni ko'rish (menyu orqali) va tezkor qidiruv. Ustoz, admin va ega uchun."""
from typing import Optional, Union

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import texts as T
from database import db
from filters import HasRole
from keyboards import ExamCb, Nav
from services import send_items
from ui import respond
from utils import academic_year, esc, exam_title, parse_query

router = Router(name="teacher")
router.message.filter(HasRole("owner", "admin", "teacher"))
router.callback_query.filter(HasRole("owner", "admin", "teacher"))

STAFF = ("owner", "admin")


# ====================== Menyu orqali: fan -> sinf -> tur ======================
async def show_subjects(target: Union[Message, CallbackQuery]) -> None:
    subjects = await db.list_subjects()
    if not subjects:
        await respond(target, T.NO_SUBJECTS)
        return
    await respond(target, T.PICK_SUBJECT, kb.browse_subjects_kb(subjects))


@router.callback_query(Nav.filter(F.step == "sub"))
async def nav_subjects(cb: CallbackQuery) -> None:
    await show_subjects(cb)


@router.callback_query(Nav.filter(F.step == "grade"))
async def nav_grade(cb: CallbackQuery, callback_data: Nav) -> None:
    subject = await db.get_subject(callback_data.sid)
    if subject is None:
        await cb.answer(T.EXAM_NOT_FOUND, show_alert=True)
        return
    await respond(
        cb,
        T.PICK_GRADE.format(subject=esc(subject["name"])),
        kb.browse_grades_kb(subject["id"]),
    )


@router.callback_query(Nav.filter(F.step == "kind"))
async def nav_kind(cb: CallbackQuery, callback_data: Nav) -> None:
    subject = await db.get_subject(callback_data.sid)
    if subject is None:
        await cb.answer(T.EXAM_NOT_FOUND, show_alert=True)
        return
    text = T.PICK_KIND.format(grade=callback_data.grade, subject=esc(subject["name"]))
    await respond(cb, text, kb.browse_kinds_kb(subject["id"], callback_data.grade))


@router.callback_query(Nav.filter(F.step == "list"))
async def nav_list(cb: CallbackQuery, callback_data: Nav) -> None:
    subject = await db.get_subject(callback_data.sid)
    kind = callback_data.kind
    if subject is None or kind not in ("BSB", "CHSB"):
        await cb.answer(T.EXAM_NOT_FOUND, show_alert=True)
        return

    sid, grade = subject["id"], callback_data.grade
    name = esc(subject["name"])
    exams = await db.list_exams(academic_year(), sid, grade, kind)

    if not exams:
        text = T.NOT_FOUND_KIND.format(grade=grade, subject=name, kind=kind)
        await respond(cb, text, kb.back_to_kind_kb(sid, grade))
    elif kind == "CHSB":
        by_quarter = {e["quarter"]: e for e in exams}
        text = T.LIST_CHSB.format(grade=grade, subject=name)
        await respond(cb, text, kb.chsb_list_kb(by_quarter, sid, grade))
    else:
        text = T.LIST_BSB.format(grade=grade, subject=name)
        await respond(cb, text, kb.bsb_list_kb(exams, sid, grade))


@router.callback_query(Nav.filter(F.step == "miss"))
async def nav_missing(cb: CallbackQuery, callback_data: Nav) -> None:
    await cb.answer(T.CHSB_MISSING.format(quarter=callback_data.q), show_alert=True)


# ====================== Imtihonni ochish ======================
@router.callback_query(ExamCb.filter(F.act == "open"))
async def exam_open(cb: CallbackQuery, callback_data: ExamCb, role: Optional[str], bot: Bot) -> None:
    exam = await db.get_exam(callback_data.id)
    if exam is None:
        await cb.answer(T.EXAM_NOT_FOUND, show_alert=True)
        return
    await cb.answer()

    chat_id = cb.from_user.id
    header = T.EXAM_HEADER.format(title=esc(exam_title(exam)), year=esc(exam["year"]))
    await bot.send_message(chat_id, header)
    await bot.send_message(chat_id, T.QUESTIONS_LABEL)
    await send_items(bot, chat_id, await db.get_items(exam["id"], "q"))
    await bot.send_message(
        chat_id, T.EXAM_AFTER, reply_markup=kb.exam_controls_kb(exam, role in STAFF)
    )


@router.callback_query(ExamCb.filter(F.act == "ans"))
async def exam_answers(cb: CallbackQuery, callback_data: ExamCb, bot: Bot) -> None:
    exam = await db.get_exam(callback_data.id)
    if exam is None:
        await cb.answer(T.EXAM_NOT_FOUND, show_alert=True)
        return
    await cb.answer()

    chat_id = cb.from_user.id
    items = await db.get_items(exam["id"], "a")
    if not items:
        await bot.send_message(chat_id, T.NO_ANSWERS)
        return
    await bot.send_message(chat_id, T.ANSWERS_LABEL)
    await send_items(bot, chat_id, items)


# ====================== Tezkor qidiruv ======================
@router.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def quick_search(message: Message) -> None:
    """Menyu tugmasi bo'lmagan har qanday matn — qidiruv so'rovi deb qaraladi."""
    subjects = await db.list_subjects()
    query = parse_query(message.text, subjects)
    if query is None:
        await message.answer(T.SEARCH_NOT_UNDERSTOOD)
        return

    exams = await db.search_exams(
        academic_year(),
        subject_ids=query.subject_ids or None,
        grade=query.grade,
        kind=query.kind,
        number=query.number,
    )
    if not exams:
        what = query.kind or "BSB/CHSB"
        await message.answer(T.SEARCH_NONE.format(what=what))
        return

    await message.answer(
        T.SEARCH_FOUND.format(count=len(exams)),
        reply_markup=kb.search_results_kb(exams, exam_title),
    )
