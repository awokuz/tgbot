"""Botni ishga tushirish:   python main.py"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.types import BotCommand

from config import ConfigError, get_settings, setup_logging
from database import db
from handlers import admin, common, gate, menu, owner, teacher
from middleware import RoleMiddleware

log = logging.getLogger("main")


async def main() -> None:
    setup_logging()
    settings = get_settings()
    await db.connect(settings.db_path, settings.owner_ids)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # SimpleEventIsolation: bir odamning xabarlari ketma-ket ishlanadi.
    # Busiz, bir nechta rasm (albom) birdaniga yuborilganda ular bir-birini buzishi mumkin.
    dp = Dispatcher(storage=MemoryStorage(), events_isolation=SimpleEventIsolation())

    # Har bir xabar va tugma bosilishidan oldin foydalanuvchi roli aniqlanadi
    dp.message.outer_middleware(RoleMiddleware())
    dp.callback_query.outer_middleware(RoleMiddleware())

    # Routerlar TARTIBI muhim: birinchi mos kelgan handler ishlaydi.
    dp.include_routers(
        common.router,    # /start, /cancel, ro'yxatdan o'tish
        menu.router,      # pastki menyu tugmalari
        owner.router,     # adminlarni boshqarish (faqat ega)
        admin.router,     # imtihon/fan qo'shish, ustozlarni boshqarish
        teacher.router,   # imtihonlarni ko'rish va qidiruv
        gate.router,      # ruxsati yo'qlar va eskirgan tugmalar
    )

    try:
        me = await bot.get_me()
        log.info("Bot ishga tushdi: @%s", me.username)
        await bot.set_my_commands([
            BotCommand(command="start", description="Boshlash / menyu"),
            BotCommand(command="cancel", description="Joriy amalni bekor qilish"),
        ])
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    except TelegramUnauthorizedError:
        print("\nXATO: BOT_TOKEN noto'g'ri. BotFather bergan tokenni .env fayliga to'g'ri nusxalang.")
    except TelegramNetworkError as exc:
        print(f"\nXATO: Telegramga ulanib bo'lmadi. Internetni tekshiring.\n({exc})")
    finally:
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ConfigError as exc:
        print(f"\nSOZLAMA XATOSI:\n{exc}\n")
    except (KeyboardInterrupt, SystemExit):
        print("\nBot to'xtatildi.")
