from functools import wraps
from mailbox import Message
from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter

from db.models import User, Role
from db.repositories.role import RoleRepository
from db.repositories.user import UserRepository


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        telegram_id = event.from_user.id

        user = await UserRepository.get_by_variable(
            tg_id=str(telegram_id)
        )

        print(f"{user=}")

        if not user:
            await event.answer(f"Вы не зарегистрированы. Ваш ID - {event.telegram_id}")
            return

        data["user"] = user
        return await handler(event, data)


class RoleFilter(BaseFilter):
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, message: Message, **data):
        user: User = data.get("user")
        print(f"{user.fio=}")

        if not user:
            return False

        role: Role = await RoleRepository.get_by_id(user.role_id)
        return role.title in self.allowed_roles