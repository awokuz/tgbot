"""Admin va ega uchun: imtihon qo'shish/o'chirish, fan qo'shish, ustozlarni boshqarish."""
import asyncio
import logging
from typing import Dict, Optional, Set, Union

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import texts as T
from database import DuplicateExam, db
from filters import HasRole
from keyboards import AddPick, ExamCb, UserCb
from services import notify_new_exam
from states import AddExam, AddSubject
from ui import respond
from utils import academic_year, esc, exam_title

log = logging.getLogger(__name__)
router = Router(name="admin")
router.message.filter(HasRole("owner", "admin"))
router.callback_query.filter(HasRole("owner", "admin"))

# Fonda ishlayotgan vazifalarni ushlab turamiz (aks holda Python ularni o'chirib yuborishi mumkin)
_background: Set["asyncio.Task[None]"] = set()

USERS_LIMIT = 60


# ====================== Imtihon qo'shish ======================
async def start_add_exam(message: Message, state: FSMContext) -> None:
    subjects = await db.list_subjects()
    if not subjects:
        await message.answer(T.NO_SUBJECTS)
        return
    await state.clear()
    await state.set_state(AddExam.subject)
    await message.answer(T.ADD_PICK_SUBJECT, reply_markup=kb.add_subjects_kb(subjects))


@router.callback_query(AddPick.filter(F.field == "cancel"))
async def add_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await respond(cb, T.ADD_CANCELLED)


@router.callback_query(AddPick.filter(F.field == "subject"), AddExam.subject)
async def add_pick_subject(cb: CallbackQuery, callback_data: AddPick, state: FSMContext) -> None:
    subject = await db.get_subject(int(callback_data.value))
    if subject is None:
        await cb.answer(T.EXAM_NOT_FOUND, show_alert=True)
        return
    await state.update_data(subject_id=subject["id"], subject_name=subject["name"])
    await state.set_state(AddExam.grade)
    await respond(cb, T.ADD_PICK_GRADE.format(subject=esc(subject["name"])), kb.add_grades_kb())


@router.callback_query(AddPick.filter(F.field == "grade"), AddExam.grade)
async def add_pick_grade(cb: CallbackQuery, callback_data: AddPick, state: FSMContext) -> None:
    await state.update_data(grade=int(callback_data.value))
    await state.set_state(AddExam.kind)
    await respond(cb, T.ADD_PICK_KIND, kb.add_kinds_kb())


@router.callback_query(AddPick.filter(F.field == "kind"), AddExam.kind)
async def add_pick_kind(cb: CallbackQuery, callback_data: AddPick, state: FSMContext) -> None:
    kind = callback_data.value
    if kind not in ("BSB", "CHSB"):
        await cb.answer(T.STALE_BUTTON, show_alert=True)
        return
    await state.update_data(kind=kind, quarter=0, replace=False)
    if kind == "CHSB":
        await state.set_state(AddExam.quarter)
        await respond(cb, T.ADD_PICK_QUARTER, kb.add_quarters_kb())
    else:
        await _ask_questions(cb, state)


@router.callback_query(AddPick.filter(F.field == "quarter"), AddExam.quarter)
async def add_pick_quarter(cb: CallbackQuery, callback_data: AddPick, state: FSMContext) -> None:
    quarter = int(callback_data.value)
    data = await state.get_data()
    await state.update_data(quarter=quarter)

    existing = await db.find_chsb(academic_year(), data["subject_id"], data["grade"], quarter)
    if existing is None:
        await _ask_questions(cb, state)
        return

    await state.set_state(AddExam.confirm)
    text = T.ADD_CHSB_EXISTS.format(
        grade=data["grade"], subject=esc(data["subject_name"]), quarter=quarter
    )
    await respond(cb, text, kb.add_replace_kb())


@router.callback_query(AddPick.filter(F.field == "replace"), AddExam.confirm)
async def add_confirm_replace(cb: CallbackQuery, callback_data: AddPick, state: FSMContext) -> None:
    if callback_data.value == "yes":
        await state.update_data(replace=True)
        await _ask_questions(cb, state)
    else:
        await state.clear()
        await respond(cb, T.ADD_CANCELLED)


async def _ask_questions(cb: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(questions=[], answers=[])
    await state.set_state(AddExam.questions)
    await respond(cb, T.ADD_SEND_QUESTIONS, kb.add_cancel_kb())


def _to_item(message: Message) -> Optional[Dict[str, str]]:
    """Xabarni saqlash uchun oddiy lug'atga aylantiradi. Qo'llab-quvvatlanmasa — None."""
    if message.photo:
        return {"ctype": "photo", "content": message.photo[-1].file_id, "caption": message.caption or ""}
    if message.document:
        return {"ctype": "document", "content": message.document.file_id, "caption": message.caption or ""}
    if message.text:
        return {"ctype": "text", "content": message.text, "caption": ""}
    return None


async def _collect(message: Message, state: FSMContext, key: str) -> None:
    if message.text and message.text.startswith("/"):
        await message.answer(T.ADD_SLASH)
        return
    item = _to_item(message)
    if item is None:
        await message.answer(T.ADD_BAD_CONTENT)
        return

    data = await state.get_data()
    items = list(data.get(key, []))
    items.append(item)
    await state.update_data(**{key: items})
    part = "q" if key == "questions" else "a"
    await message.answer(T.ADD_ITEM_OK.format(n=len(items)), reply_markup=kb.add_done_kb(part))


@router.message(AddExam.questions)
async def collect_questions(message: Message, state: FSMContext) -> None:
    await _collect(message, state, "questions")


@router.message(AddExam.answers)
async def collect_answers(message: Message, state: FSMContext) -> None:
    await _collect(message, state, "answers")


@router.callback_query(AddPick.filter(F.field == "done"), AddExam.questions)
async def done_questions(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("questions"):
        await cb.answer(T.ADD_NEED_QUESTIONS, show_alert=True)
        return
    await state.set_state(AddExam.answers)
    await respond(cb, T.ADD_SEND_ANSWERS, kb.add_done_kb("a", has_items=False))


@router.callback_query(AddPick.filter(F.field == "done"), AddExam.answers)
async def done_answers(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.clear()  # avval tozalaymiz: tugma ikki marta bosilsa, ikki marta saqlanmasin

    try:
        exam_id = await db.add_exam(
            year=academic_year(),
            subject_id=data["subject_id"],
            grade=data["grade"],
            kind=data["kind"],
            quarter=data.get("quarter", 0),
            created_by=cb.from_user.id,
            questions=data["questions"],
            answers=data.get("answers", []),
            replace=data.get("replace", False),
        )
    except DuplicateExam:
        await respond(cb, T.ADD_DUPLICATE)
        return

    exam = await db.get_exam(exam_id)
    await respond(cb, T.ADD_SAVED.format(title=esc(exam_title(exam))))

    task = asyncio.create_task(notify_new_exam(bot, exam, exclude_id=cb.from_user.id))
    _background.add(task)
    task.add_done_callback(_background.discard)


# ====================== Imtihonni o'chirish ======================
@router.callback_query(ExamCb.filter(F.act == "del"))
async def exam_delete_ask(cb: CallbackQuery, callback_data: ExamCb) -> None:
    exam = await db.get_exam(callback_data.id)
    if exam is None:
        await cb.answer(T.EXAM_NOT_FOUND, show_alert=True)
        return
    text = T.CONFIRM_DELETE_EXAM.format(title=esc(exam_title(exam)))
    await respond(cb, text, kb.confirm_delete_exam_kb(exam["id"]))


@router.callback_query(ExamCb.filter(F.act == "delyes"))
async def exam_delete_yes(cb: CallbackQuery, callback_data: ExamCb) -> None:
    await db.delete_exam(callback_data.id)
    await respond(cb, T.EXAM_DELETED)


# ====================== Fan qo'shish ======================
async def start_add_subject(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddSubject.name)
    await message.answer(T.SUBJECT_ASK)


@router.message(AddSubject.name, F.text, ~F.text.startswith("/"))
async def subject_name(message: Message, state: FSMContext) -> None:
    name = " ".join(message.text.split())
    if not 2 <= len(name) <= 40:
        await message.answer(T.SUBJECT_BAD)
        return
    subject_id = await db.add_subject(name)
    await state.clear()
    if subject_id is None:
        await message.answer(T.SUBJECT_EXISTS)
    else:
        await message.answer(T.SUBJECT_ADDED.format(name=esc(name)))


@router.message(AddSubject.name)
async def subject_name_not_text(message: Message) -> None:
    await message.answer(T.SUBJECT_TEXT_ONLY)


# ====================== Ustozlarni boshqarish ======================
def _can_manage(role: Optional[str], user: Dict) -> bool:
    """Ega — hammani; admin — faqat oddiy ustozlarni boshqara oladi."""
    if db.is_owner(user["user_id"]):
        return False
    if user["is_admin"]:
        return role == "owner"
    return True


async def show_users(target: Union[Message, CallbackQuery]) -> None:
    users = await db.list_users()
    if not users:
        await respond(target, T.USERS_EMPTY)
        return
    counts = {"pending": 0, "approved": 0, "blocked": 0}
    for u in users:
        counts[u["status"]] = counts.get(u["status"], 0) + 1
    text = T.USERS_TITLE.format(**counts)
    if len(users) > USERS_LIMIT:
        text += T.USERS_MORE.format(limit=USERS_LIMIT)
    await respond(target, text, kb.users_kb(users[:USERS_LIMIT]))


@router.callback_query(UserCb.filter(F.act == "list"))
async def users_list(cb: CallbackQuery) -> None:
    await show_users(cb)


@router.callback_query(UserCb.filter(F.act == "view"))
async def user_view(cb: CallbackQuery, callback_data: UserCb, role: Optional[str]) -> None:
    user = await db.get_user(callback_data.id)
    if user is None:
        await cb.answer(T.USER_NOT_FOUND, show_alert=True)
        return
    username = f" · @{user['username']}" if user["username"] else ""
    text = T.USER_CARD.format(
        name=esc(user["full_name"]),
        uid=user["user_id"],
        username=esc(username),
        status=T.STATUS_LABELS.get(user["status"], user["status"]),
    )
    await respond(cb, text, kb.user_card_kb(user, _can_manage(role, user)))


@router.callback_query(UserCb.filter(F.act.in_({"approve", "reject", "block", "unblock", "del", "delyes"})))
async def user_action(cb: CallbackQuery, callback_data: UserCb, role: Optional[str], bot: Bot) -> None:
    uid = callback_data.id
    act = callback_data.act
    user = await db.get_user(uid)
    if user is None:
        await cb.answer(T.USER_NOT_FOUND, show_alert=True)
        return
    if not _can_manage(role, user):
        await cb.answer(T.USER_NO_RIGHT, show_alert=True)
        return

    name = esc(user["full_name"])

    if act in ("approve", "reject") and user["status"] != "pending":
        # Boshqa admin allaqachon javob bergan
        await cb.answer(T.REQUEST_ALREADY_DONE, show_alert=True)
        return

    if act == "approve":
        await db.set_status(uid, "approved")
        await _notify(bot, uid, T.APPROVED_USER.format(name=name), kb.main_menu("teacher"))
        await respond(cb, T.REQUEST_APPROVED_ADMIN.format(name=name), kb.user_back_kb())
    elif act == "reject":
        await db.delete_user(uid)  # o'chirilsa, odam /start bosib qaytadan so'rov yubora oladi
        await _notify(bot, uid, T.REJECTED_USER)
        await respond(cb, T.REQUEST_REJECTED_ADMIN.format(name=name), kb.user_back_kb())
    elif act == "block":
        await db.set_status(uid, "blocked")
        await _notify(bot, uid, T.BLOCKED_NOTICE)
        await respond(cb, T.USER_BLOCKED_ADMIN.format(name=name), kb.user_back_kb())
    elif act == "unblock":
        await db.set_status(uid, "approved")
        await _notify(bot, uid, T.UNBLOCKED_NOTICE)
        await respond(cb, T.USER_UNBLOCKED_ADMIN.format(name=name), kb.user_back_kb())
    elif act == "del":
        await respond(cb, T.USER_CONFIRM_DELETE.format(name=name), kb.user_confirm_delete_kb(uid))
    else:  # delyes
        await db.delete_user(uid)
        await respond(cb, T.USER_DELETED_ADMIN.format(name=name), kb.user_back_kb())


async def _notify(bot: Bot, user_id: int, text: str, reply_markup=None) -> None:
    try:
        await bot.send_message(user_id, text, reply_markup=reply_markup)
    except TelegramAPIError:
        log.warning("Foydalanuvchi %s ga xabar yuborib bo'lmadi", user_id)
