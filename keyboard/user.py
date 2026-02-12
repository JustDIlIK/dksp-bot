from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from db.repositories.tool import ToolRepository
from db.repositories.vehicle import VehicleRepository


async def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить данные")]], resize_keyboard=True
    )

    return keyboard


async def get_save_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Сохранить")]], resize_keyboard=True
    )

    return keyboard


async def get_tools_keyboard():
    tools = await ToolRepository.get_all()

    buttons = [KeyboardButton(text=tool.title) for tool in tools]

    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_vehicles_keyboard():
    vehicles = await VehicleRepository.get_all()

    buttons = [
        KeyboardButton(text=f"{vehicle.model} - {vehicle.number}")
        for vehicle in vehicles
    ]

    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    buttons.append(KeyboardButton(text="Отмена"))

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
