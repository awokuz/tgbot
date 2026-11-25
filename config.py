"""Bot sozlamalari. Hammasi .env faylidan o'qiladi (tokenni kodga yozmang!)."""
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


class ConfigError(Exception):
    """Sozlamalarda xato bo'lsa ko'tariladi."""


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_ids: Tuple[int, ...]
    db_path: str
    tz_offset_hours: int


def _parse_ids(raw: str) -> Tuple[int, ...]:
    ids = []
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return tuple(ids)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # utf-8-sig: Windows Bloknoti saqlaydigan ko'rinmas belgini ham tushunadi
    load_dotenv(BASE_DIR / ".env", encoding="utf-8-sig")

    token = os.getenv("BOT_TOKEN", "").strip()
    if ":" not in token:
        raise ConfigError(
            "BOT_TOKEN topilmadi yoki noto'g'ri.\n"
            "  1) .env.example faylidan nusxa olib, nomini .env qiling\n"
            "  2) BOT_TOKEN= dan keyin @BotFather bergan tokenni yozing"
        )

    owners = _parse_ids(os.getenv("OWNER_IDS", "") or os.getenv("OWNER_ID", ""))
    if not owners:
        raise ConfigError(
            "OWNER_IDS topilmadi.\n"
            "  .env faylida OWNER_IDS= dan keyin o'z Telegram ID raqamingizni yozing\n"
            "  (ID ni @userinfobot dan bilib olasiz)"
        )

    try:
        tz_offset = int(os.getenv("TZ_OFFSET", "5"))
    except ValueError:
        raise ConfigError("TZ_OFFSET butun son bo'lishi kerak (O'zbekiston uchun 5).")

    db_path = os.getenv("DB_PATH", "").strip() or str(BASE_DIR / "bot.db")
    return Settings(
        bot_token=token,
        owner_ids=owners,
        db_path=db_path,
        tz_offset_hours=tz_offset,
    )


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
