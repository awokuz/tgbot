"""Barcha tugmalar (pastki menyu va xabar ostidagi inline tugmalar) shu yerda."""
from typing import Callable, Dict, List, Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

import texts as T

# ====================== Tugma bosilganda keladigan ma'lumotlar ======================
# Telegram callback_data uchun 64 baytgacha joy beradi, shuning uchun nomlar qisqa.


class Nav(CallbackData, prefix="nav"):
    """Imtihonlarni ko'rish: fan -> sinf -> tur -> ro'yxat."""
    step: str            # sub | grade | kind | list | miss
    sid: int = 0         # fan id
    grade: int = 0       # sinf
    kind: str = ""       # BSB | CHSB
    q: int = 0           # chorak (faqat "miss" uchun)


class ExamCb(CallbackData, prefix="ex"):
    """Bitta imtihon ustida amallar."""
    id: int
    act: str             # open | ans | del | delyes


class AddPick(CallbackData, prefix="ap"):
    """Imtihon qo'shish jarayonidagi tanlovlar."""
    field: str           # subject | grade | kind | quarter | replace | done | cancel
    value: str = ""


class UserCb(CallbackData, prefix="us"):
    """Ustozlarni boshqarish."""
    id: int = 0
    act: str = "list"    # list | view | approve | reject | block | unblock | del | delyes


class OwnerCb(CallbackData, prefix="ow"):
    """Adminlarni boshqarish (faqat ega)."""
    act: str             # list | add | rm | rmyes
    id: int = 0


# ====================== Yordamchilar ======================
def _btn(text: str, data: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data.pack())


def _grid(buttons: List[InlineKeyboardButton], per_row: int) -> List[List[InlineKeyboardButton]]:
    return [buttons[i:i + per_row] for i in range(0, len(buttons), per_row)]


def _markup(rows: List[List[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _short(text: str, limit: int = 40) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


# ====================== Pastki menyu ======================
def main_menu(role: str) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=T.BTN_EXAMS), KeyboardButton(text=T.BTN_SEARCH)]]
    if role in ("owner", "admin"):
        rows.append([KeyboardButton(text=T.BTN_ADD_EXAM), KeyboardButton(text=T.BTN_ADD_SUBJECT)])
        staff_row = [KeyboardButton(text=T.BTN_USERS)]
        if role == "owner":
            staff_row.append(KeyboardButton(text=T.BTN_ADMINS))
        rows.append(staff_row)
    rows.append([KeyboardButton(text=T.BTN_HELP)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# ====================== Imtihonlarni ko'rish ======================
def subjects_kb(
    subjects: List[Dict],
    make_cb: Callable[[int], CallbackData],
    extra: Optional[List[List[InlineKeyboardButton]]] = None,
) -> InlineKeyboardMarkup:
    buttons = [_btn(s["name"], make_cb(s["id"])) for s in subjects]
    return _markup(_grid(buttons, 2) + (extra or []))


def grades_kb(
    make_cb: Callable[[int], CallbackData],
    extra: Optional[List[List[InlineKeyboardButton]]] = None,
) -> InlineKeyboardMarkup:
    buttons = [_btn(f"{g}-sinf", make_cb(g)) for g in range(1, 12)]
    return _markup(_grid(buttons, 4) + (extra or []))


def back_row(data: CallbackData, text: str = "⬅️ Orqaga") -> List[InlineKeyboardButton]:
    return [_btn(text, data)]


def browse_subjects_kb(subjects: List[Dict]) -> InlineKeyboardMarkup:
    return subjects_kb(subjects, lambda sid: Nav(step="grade", sid=sid))


def browse_grades_kb(sid: int) -> InlineKeyboardMarkup:
    return grades_kb(
        lambda g: Nav(step="kind", sid=sid, grade=g),
        extra=[back_row(Nav(step="sub"))],
    )


def browse_kinds_kb(sid: int, grade: int) -> InlineKeyboardMarkup:
    row = [
        _btn("📝 BSB", Nav(step="list", sid=sid, grade=grade, kind="BSB")),
        _btn("🗓 CHSB", Nav(step="list", sid=sid, grade=grade, kind="CHSB")),
    ]
    return _markup([row, back_row(Nav(step="grade", sid=sid))])


def back_to_kind_kb(sid: int, grade: int) -> InlineKeyboardMarkup:
    return _markup([back_row(Nav(step="kind", sid=sid, grade=grade))])


def bsb_list_kb(exams: List[Dict], sid: int, grade: int) -> InlineKeyboardMarkup:
    buttons = [_btn(f"BSB-{e['number']}", ExamCb(id=e["id"], act="open")) for e in exams]
    return _markup(_grid(buttons, 3) + [back_row(Nav(step="kind", sid=sid, grade=grade))])


def chsb_list_kb(by_quarter: Dict[int, Dict], sid: int, grade: int) -> InlineKeyboardMarkup:
    buttons = []
    for q in (1, 2, 3, 4):
        exam = by_quarter.get(q)
        if exam is not None:
            buttons.append(_btn(f"✅ {q}-chorak", ExamCb(id=exam["id"], act="open")))
        else:
            buttons.append(_btn(f"➖ {q}-chorak", Nav(step="miss", sid=sid, grade=grade, kind="CHSB", q=q)))
    return _markup(_grid(buttons, 2) + [back_row(Nav(step="kind", sid=sid, grade=grade))])


def exam_controls_kb(exam: Dict, is_staff: bool) -> InlineKeyboardMarkup:
    rows = [
        [_btn("✅ Javoblarni ko'rish", ExamCb(id=exam["id"], act="ans"))],
        back_row(
            Nav(step="list", sid=exam["subject_id"], grade=exam["grade"], kind=exam["kind"]),
            "⬅️ Ro'yxatga qaytish",
        ),
    ]
    if is_staff:
        rows.append([_btn("🗑 O'chirish", ExamCb(id=exam["id"], act="del"))])
    return _markup(rows)


def confirm_delete_exam_kb(exam_id: int) -> InlineKeyboardMarkup:
    return _markup([[
        _btn("🗑 Ha, o'chir", ExamCb(id=exam_id, act="delyes")),
        _btn("↩️ Yo'q", ExamCb(id=exam_id, act="open")),
    ]])


def search_results_kb(exams: List[Dict], title_fn: Callable[[Dict], str]) -> InlineKeyboardMarkup:
    rows = [[_btn(_short(title_fn(e), 60), ExamCb(id=e["id"], act="open"))] for e in exams]
    return _markup(rows)


# ====================== Imtihon qo'shish (admin) ======================
def cancel_row() -> List[InlineKeyboardButton]:
    return [_btn("❌ Bekor qilish", AddPick(field="cancel"))]


def add_subjects_kb(subjects: List[Dict]) -> InlineKeyboardMarkup:
    return subjects_kb(
        subjects, lambda sid: AddPick(field="subject", value=str(sid)), extra=[cancel_row()]
    )


def add_grades_kb() -> InlineKeyboardMarkup:
    return grades_kb(lambda g: AddPick(field="grade", value=str(g)), extra=[cancel_row()])


def add_kinds_kb() -> InlineKeyboardMarkup:
    row = [
        _btn("📝 BSB", AddPick(field="kind", value="BSB")),
        _btn("🗓 CHSB", AddPick(field="kind", value="CHSB")),
    ]
    return _markup([row, cancel_row()])


def add_quarters_kb() -> InlineKeyboardMarkup:
    buttons = [_btn(f"{q}-chorak", AddPick(field="quarter", value=str(q))) for q in (1, 2, 3, 4)]
    return _markup(_grid(buttons, 2) + [cancel_row()])


def add_replace_kb() -> InlineKeyboardMarkup:
    return _markup([
        [
            _btn("🔄 Ha, almashtir", AddPick(field="replace", value="yes")),
            _btn("↩️ Yo'q", AddPick(field="replace", value="no")),
        ],
    ])


def add_cancel_kb() -> InlineKeyboardMarkup:
    return _markup([cancel_row()])


def add_done_kb(part: str, has_items: bool = True) -> InlineKeyboardMarkup:
    """part: 'q' (savollar) yoki 'a' (javoblar)."""
    if part == "q":
        label = "✅ Savollar tayyor"
    else:
        label = "✅ Javoblar tayyor" if has_items else "⏭ Javobsiz saqlash"
    return _markup([[_btn(label, AddPick(field="done", value=part))], cancel_row()])


# ====================== Ustozlarni boshqarish ======================
def request_kb(uid: int) -> InlineKeyboardMarkup:
    return _markup([[
        _btn("✅ Qabul qilish", UserCb(id=uid, act="approve")),
        _btn("❌ Rad etish", UserCb(id=uid, act="reject")),
    ]])


_STATUS_ICON = {"pending": "⏳", "approved": "✅", "blocked": "🚫"}


def users_kb(users: List[Dict]) -> InlineKeyboardMarkup:
    rows = [
        [_btn(f"{_STATUS_ICON.get(u['status'], '•')} {_short(u['full_name'])}", UserCb(id=u["user_id"], act="view"))]
        for u in users
    ]
    return _markup(rows)


def user_card_kb(user: Dict, can_manage: bool) -> InlineKeyboardMarkup:
    uid = user["user_id"]
    rows: List[List[InlineKeyboardButton]] = []
    if can_manage:
        if user["status"] == "pending":
            rows.append([
                _btn("✅ Qabul qilish", UserCb(id=uid, act="approve")),
                _btn("❌ Rad etish", UserCb(id=uid, act="reject")),
            ])
        elif user["status"] == "approved":
            rows.append([
                _btn("🚫 Bloklash", UserCb(id=uid, act="block")),
                _btn("🗑 O'chirish", UserCb(id=uid, act="del")),
            ])
        else:
            rows.append([
                _btn("🔓 Blokdan chiqarish", UserCb(id=uid, act="unblock")),
                _btn("🗑 O'chirish", UserCb(id=uid, act="del")),
            ])
    rows.append(back_row(UserCb(id=0, act="list"), "⬅️ Ro'yxatga qaytish"))
    return _markup(rows)


def user_back_kb() -> InlineKeyboardMarkup:
    return _markup([back_row(UserCb(id=0, act="list"), "⬅️ Ro'yxatga qaytish")])


def user_confirm_delete_kb(uid: int) -> InlineKeyboardMarkup:
    return _markup([[
        _btn("🗑 Ha, o'chir", UserCb(id=uid, act="delyes")),
        _btn("↩️ Yo'q", UserCb(id=uid, act="view")),
    ]])


# ====================== Adminlar (faqat ega) ======================
def admins_kb(admins: List[Dict]) -> InlineKeyboardMarkup:
    rows = [
        [_btn(f"➖ {_short(a['full_name'])}", OwnerCb(act="rm", id=a["user_id"]))]
        for a in admins
    ]
    rows.append([_btn("➕ Admin qo'shish", OwnerCb(act="add"))])
    return _markup(rows)


def admin_confirm_remove_kb(uid: int) -> InlineKeyboardMarkup:
    return _markup([[
        _btn("➖ Ha, olib tashla", OwnerCb(act="rmyes", id=uid)),
        _btn("↩️ Yo'q", OwnerCb(act="list")),
    ]])


def admins_back_kb() -> InlineKeyboardMarkup:
    return _markup([back_row(OwnerCb(act="list"), "⬅️ Adminlarga qaytish")])
