"""Suhbat bosqichlari (FSM): bot foydalanuvchidan nima kutayotganini shu yerdan biladi."""
from aiogram.fsm.state import State, StatesGroup


class Reg(StatesGroup):
    name = State()          # ustoz ism-familiyasini yozmoqda


class AddExam(StatesGroup):
    subject = State()       # fan tanlash
    grade = State()         # sinf tanlash
    kind = State()          # BSB yoki CHSB
    quarter = State()       # CHSB uchun chorak
    confirm = State()       # CHSB allaqachon bor — almashtiraymi?
    questions = State()     # savollarni yuborish
    answers = State()       # javoblarni yuborish


class AddSubject(StatesGroup):
    name = State()          # yangi fan nomi


class AddAdmin(StatesGroup):
    user_id = State()       # yangi adminning Telegram ID si
