from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from db.models import User
from db.repositories.tool import ToolRepository
from db.repositories.user import UserRepository
from db.repositories.vehicle import VehicleRepository


async def get_moderator_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Получить отчет")],
            [KeyboardButton(text="Пользователи")],
            [KeyboardButton(text="Роли")],
            [KeyboardButton(text="Типы товаров")],
            [KeyboardButton(text="Техники")],
        ],
        resize_keyboard=True,
    )

    return keyboard

def get_crud_menu(entity: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"Создать {entity}")],
            [KeyboardButton(text=f"Список {entity}")],
            [KeyboardButton(text=f"Удалить {entity}")],
            [KeyboardButton(text="Главное меню")],
        ],
        resize_keyboard=True,
    )

async def get_moderator_report_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отчет по машине")],
            [KeyboardButton(text="Отчет по пользователю")],
            [KeyboardButton(text="Отчет по типу")],
            [KeyboardButton(text="Главное меню")],
        ],
        resize_keyboard=True,
    )

    return keyboard


async def get_users_list_keyboard():

    users = await UserRepository.get_all()

    buttons = [KeyboardButton(text=user.fio) for user in users]

    keyboard = [buttons[i : i + 3] for i in range(0, len(buttons), 2)]
    buttons.append(KeyboardButton(text="Главное меню"))

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_tools_keyboard():
    tools = await ToolRepository.get_all()

    buttons = [KeyboardButton(text=tool.title) for tool in tools]

    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    buttons.append(KeyboardButton(text="Главное меню"))

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_vehicles_keyboard():
    vehicles = await VehicleRepository.get_all()

    buttons = [
        KeyboardButton(text=f"{vehicle.model} - {vehicle.number}")
        for vehicle in vehicles
    ]

    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    buttons.append(KeyboardButton(text="Главное меню"))

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_pagination_keyboard(page: int, total_pages: int):
    buttons = []

    if page > 1:
        buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"reports:{page-1}")
        )

    if page < total_pages:
        buttons.append(
            InlineKeyboardButton(text="➡️ Вперед", callback_data=f"reports:{page+1}")
        )

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_reports_keyboard(reports, page, total_pages):
    keyboard = []

    for report in reports:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"Подробнее №{report.id}",
                    callback_data=f"report_detail:{report.id}",
                )
            ]
        )

    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"reports:{page-1}")
        )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(text="➡️", callback_data=f"reports:{page+1}")
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
