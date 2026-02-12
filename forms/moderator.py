from aiogram.fsm.state import StatesGroup, State

from db.repositories.report import ReportRepository
from keyboard.moderator import get_pagination_keyboard, get_reports_keyboard

class ReportForm(StatesGroup):
    start = State()
    finish = State()

class RoleForm(StatesGroup):
    create_title = State()
    edit_title = State()

class ToolForm(StatesGroup):
    create_title = State()
    edit_title = State()

class VehicleForm(StatesGroup):
    create_model = State()
    create_number = State()

    edit_model = State()
    edit_number = State()

class UserForm(StatesGroup):
    create_fio = State()
    create_tg_id = State()
    create_role = State()

    edit_fio = State()
    edit_tg_id = State()
    edit_role = State()


PER_PAGE = 5


async def send_reports_page(message, page: int, edit: bool = False, **filters):
    reports, total = await ReportRepository.get_paginated(
        page=page,
        per_page=PER_PAGE,
        **filters
    )

    if not reports:
        await message.answer("Отчеты не найдены")
        return

    total_pages = (total + PER_PAGE - 1) // PER_PAGE

    text = [f"📄 Отчеты (стр. {page} из {total_pages})\n"]

    for report in reports:
        text.append(
            f"№{report.id} | "
            f"{report.user.fio} | "
            f"{report.created_at:%d.%m.%Y}"
        )

    keyboard = get_reports_keyboard(reports, page, total_pages)

    if edit:
        await message.edit_text(
            "\n".join(text),
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "\n".join(text),
            reply_markup=keyboard
        )