"""Rol bo'yicha filtr: handler faqat kerakli rolga ega odamlar uchun ishlaydi."""
from typing import Optional

from aiogram.filters import BaseFilter


class HasRole(BaseFilter):
    """HasRole("owner", "admin") — faqat ega va adminlar uchun.

    Foydalanuvchi roli RoleMiddleware tomonidan `role` nomi bilan beriladi.
    None — hali ro'yxatdan o'tmagan odam.
    """

    def __init__(self, *roles: Optional[str]) -> None:
        self.roles = frozenset(roles)

    async def __call__(self, event, role: Optional[str] = None) -> bool:  # type: ignore[override]
        return role in self.roles
