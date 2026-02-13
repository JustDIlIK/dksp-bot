from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.models import Role
from db.repositories.role import RoleRepository
from keyboard.moderator import get_moderator_main_keyboard
from keyboard.user import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, user, state: FSMContext):
    role: Role = await RoleRepository.get_by_id(user.role_id)
    await state.clear()
    if role.title == "user":
        keyboard = await get_main_keyboard()
        await message.answer(
            f"Здравствуйте, {user.fio} 👋",
            reply_markup=keyboard
        )
    elif role.title == "moderator":
        keyboard = await get_moderator_main_keyboard()
        await message.answer(
            f"Здравствуйте, модератор {user.fio} 👨‍💼",
            reply_markup=keyboard
        )
    elif role.title == "admin":
        # keyboard = await get_moderator_main_keyboard()
        await message.answer(
            f"Здравствуйте, админ {user.fio} 👨‍💼",
            # reply_markup=keyboard
        )
    else:
        await message.answer("Нет доступа")
