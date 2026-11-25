"""Kichik yordamchi: xabarni yuborish yoki (tugma bosilgan bo'lsa) tahrirlash."""
from typing import Optional, Union

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def respond(
    target: Union[Message, CallbackQuery],
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """Message bo'lsa — yangi xabar yuboradi. CallbackQuery bo'lsa — bosilgan xabarni yangilaydi."""
    if isinstance(target, Message):
        await target.answer(text, reply_markup=reply_markup)
        return

    msg = target.message
    try:
        if isinstance(msg, Message):
            await msg.edit_text(text, reply_markup=reply_markup)
        else:
            await target.bot.send_message(target.from_user.id, text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        # Matn aynan bir xil bo'lsa Telegram xato beradi — bu odatiy holat, e'tibor bermaymiz.
        if "message is not modified" not in str(exc):
            await target.bot.send_message(target.from_user.id, text, reply_markup=reply_markup)
    await target.answer()
