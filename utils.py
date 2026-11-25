"""Yordamchi funksiyalar: o'quv yili, matnni tozalash, qidiruv so'rovini tushunish."""
import html
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, NamedTuple, Optional, Set

from config import get_settings

esc = html.escape  # foydalanuvchi matnini HTML ga xavfsiz qo'yish uchun


def academic_year() -> str:
    """Hozirgi o'quv yili. Sentabrdan yangi yil boshlanadi: 2026-oktabr -> '2026-2027'."""
    tz = timezone(timedelta(hours=get_settings().tz_offset_hours))
    now = datetime.now(tz)
    start = now.year if now.month >= 9 else now.year - 1
    return f"{start}-{start + 1}"


def exam_title(exam: Dict) -> str:
    """Oddiy matn (tugmalarda ham ishlatiladi). HTML xabarga qo'yishda esc() qiling."""
    head = f"{exam['grade']}-sinf · {exam['subject_name']} · "
    if exam["kind"] == "BSB":
        return head + f"BSB-{exam['number']}"
    return head + f"CHSB · {exam['quarter']}-chorak"


# ---------- qidiruv ----------
_APOSTROPHES = str.maketrans(
    {"ʻ": "'", "ʼ": "'", "‘": "'", "’": "'", "`": "'", "´": "'", "′": "'"}
)

SINF_WORDS = {"sinf", "sinfi", "sinfda", "klass"}
SKIP_WORDS = {"imtihon", "imtihoni", "savol", "savollari", "javob", "javoblari", "va", "uchun"}


def normalize(text: str) -> str:
    """Kichik harf + hamma xil apostrofni bitta ko'rinishga keltiradi (o', oʻ, o‘ -> o')."""
    return text.translate(_APOSTROPHES).lower().strip()


class Query(NamedTuple):
    grade: Optional[int]
    kind: Optional[str]
    number: Optional[int]
    subject_ids: List[int]


def _subject_matches(token: str, name: str) -> bool:
    if len(token) < 3:
        return False
    return any(word.startswith(token) for word in normalize(name).split())


def parse_query(text: str, subjects: List[Dict]) -> Optional[Query]:
    """'7 algebra bsb 3' kabi gapni tushunadi. Hech narsa tushunmasa None qaytaradi."""
    tokens = re.findall(r"[\w']+", normalize(text).replace("-", " "))
    grade: Optional[int] = None
    kind: Optional[str] = None
    number: Optional[int] = None
    subject_sets: List[Set[int]] = []

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        m = re.fullmatch(r"(bsb|chsb)(\d+)?", tok)
        if m:
            kind = m.group(1).upper()
            if m.group(2):
                number = int(m.group(2))
            elif nxt.isdigit():
                number = int(nxt)
                i += 1
        elif tok.isdigit():
            n = int(tok)
            if nxt in SINF_WORDS and 1 <= n <= 11:
                grade = n
                i += 1
            elif nxt == "chorak":
                number = n
                i += 1
            elif grade is None and 1 <= n <= 11:
                grade = n
            elif number is None:
                number = n
        elif tok in SINF_WORDS or tok in SKIP_WORDS or tok == "chorak":
            pass
        else:
            ids = {s["id"] for s in subjects if _subject_matches(tok, s["name"])}
            if ids:
                subject_sets.append(ids)
        i += 1

    subject_ids: List[int] = []
    if subject_sets:
        common = set.intersection(*subject_sets)
        chosen = common if common else set.union(*subject_sets)
        subject_ids = sorted(chosen)

    if grade is None and kind is None and number is None and not subject_ids:
        return None
    return Query(grade, kind, number, subject_ids)
