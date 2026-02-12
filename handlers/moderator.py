import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from db.repositories.report import ReportRepository
from db.repositories.role import RoleRepository
from db.repositories.tool import ToolRepository
from db.repositories.user import UserRepository
from db.repositories.vehicle import VehicleRepository
from forms.moderator import (
    ReportForm,
    send_reports_page,
    RoleForm,
    ToolForm,
    VehicleForm,
    UserForm,
)
from keyboard.moderator import (
    get_users_list_keyboard,
    get_moderator_report_keyboard,
    get_moderator_main_keyboard,
    get_vehicles_keyboard,
    get_tools_keyboard,
    get_crud_menu,
)
from middleware import RoleFilter

router = Router()

REPORT_TYPES = {
    "Отчет по машине": ("vehicle", get_vehicles_keyboard),
    "Отчет по пользователю": ("user", get_users_list_keyboard),
    "Отчет по типу": ("tool", get_tools_keyboard),
}


def get_repository(entity: str):

    print(f"{entity=}")


    return {
        "users": UserRepository,
        "roles": RoleRepository,
        "tools": ToolRepository,
        "vehicles": VehicleRepository,
    }.get(entity)


@router.message(F.text == "Главное меню", RoleFilter(["moderator"]))
async def cancel_form(message: Message, state: FSMContext):
    keyboard = await get_moderator_main_keyboard()
    await state.clear()
    await message.answer("Главное меню", reply_markup=keyboard)


##############################
@router.message(F.text == "Роли", RoleFilter(["moderator"]))
async def roles_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Список", callback_data="roles:list")],
            [InlineKeyboardButton(text="➕ Добавить", callback_data="roles:create")]
        ]
    )
    await message.answer("Управление ролями:", reply_markup=keyboard)


@router.callback_query(F.data == "roles:list")
async def list_roles(callback: CallbackQuery):
    roles = await RoleRepository.get_all()

    if not roles:
        await callback.message.answer("Роли не найдены")
        await callback.answer()
        return

    keyboard = []

    for role in roles:
        keyboard.append([
            InlineKeyboardButton(
                text=role.title,
                callback_data=f"role:detail:{role.id}"
            )
        ])

    await callback.message.answer(
        "📋 Список ролей:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("role:detail:"))
async def role_detail(callback: CallbackQuery):
    role_id = int(callback.data.split(":")[2])
    role = await RoleRepository.get_by_id(role_id)

    if not role:
        await callback.answer("Не найдено", show_alert=True)
        return

    text = f"🎭 Роль: {role.title}"

    keyboard = []

    if role.title != "admin":
        keyboard.append([
            InlineKeyboardButton(
                text="✏ Редактировать",
                callback_data=f"role:edit:{role.id}"
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                text="❌ Удалить",
                callback_data=f"role:delete:{role.id}"
            )
        ])

    await callback.message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@router.callback_query(F.data == "roles:create")
async def create_role_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RoleForm.create_title)
    await callback.message.answer("Введите название роли:")
    await callback.answer()


@router.message(RoleForm.create_title)
async def create_role_finish(message: Message, state: FSMContext):
    title = message.text.strip().lower()

    exists = await RoleRepository.get_by_variable(title=title)

    if exists:
        await message.answer("❌ Такая роль уже существует")
        return

    await RoleRepository.add_record(title=title)

    await message.answer("✅ Роль создана")
    await state.clear()


@router.callback_query(F.data.startswith("role:edit:"))
async def edit_role_start(callback: CallbackQuery, state: FSMContext):
    role_id = int(callback.data.split(":")[2])
    role = await RoleRepository.get_by_id(role_id)

    if role.title == "admin":
        await callback.answer("Админа менять нельзя", show_alert=True)
        return

    await state.update_data(edit_role_id=role_id)
    await state.set_state(RoleForm.edit_title)

    await callback.message.answer("Введите новое название роли:")
    await callback.answer()


@router.message(RoleForm.edit_title)
async def edit_role_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    new_title = message.text.strip().lower()

    exists = await RoleRepository.get_by_variable(title=new_title)
    if exists and exists.id != data["edit_role_id"]:
        await message.answer("❌ Такая роль уже существует")
        return

    await RoleRepository.update_record(
        id=data["edit_role_id"],
        title=new_title
    )

    await message.answer("✅ Роль обновлена")
    await state.clear()


@router.callback_query(F.data.startswith("role:delete:"))
async def confirm_delete_role(callback: CallbackQuery):
    role_id = int(callback.data.split(":")[2])
    role = await RoleRepository.get_by_id(role_id)

    if role.title == "admin":
        await callback.answer("Админа удалить нельзя", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data=f"role:delete_confirm:{role_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="role:delete_cancel"
                )
            ]
        ]
    )

    await callback.message.answer("Удалить роль?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("role:delete_confirm:"))
async def delete_role(callback: CallbackQuery):
    role_id = int(callback.data.split(":")[2])

    users = await UserRepository.get_all_by_variable(role_id=role_id)

    if users:
        await callback.answer("Есть пользователи с этой ролью!", show_alert=True)
        return

    await RoleRepository.delete_by_id(role_id)

    await callback.message.answer("❌ Роль удалена")
    await callback.answer()

router.callback_query(F.data == "role:delete_cancel")
async def cancel_delete_role(callback: CallbackQuery):
    await callback.message.answer("Удаление отменено")
    await callback.answer()

##############################

@router.message(F.text == "Типы товаров", RoleFilter(["moderator"]))
async def tools_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Список", callback_data="tools:list")],
            [InlineKeyboardButton(text="➕ Добавить", callback_data="tools:create")]
        ]
    )
    await message.answer("Управление типами товаров:", reply_markup=keyboard)

@router.callback_query(F.data == "tools:list")
async def list_tools(callback: CallbackQuery):
    tools = await ToolRepository.get_all()

    if not tools:
        await callback.message.answer("Типы товаров не найдены")
        await callback.answer()
        return

    keyboard = []

    for tool in tools:
        keyboard.append([
            InlineKeyboardButton(
                text=tool.title,
                callback_data=f"tool:detail:{tool.id}"
            )
        ])

    await callback.message.answer(
        "📋 Список типов товаров:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("tool:detail:"))
async def tool_detail(callback: CallbackQuery):
    tool_id = int(callback.data.split(":")[2])
    tool = await ToolRepository.get_by_id(tool_id)

    if not tool:
        await callback.answer("Не найдено", show_alert=True)
        return

    text = f"🛠 Тип товара: {tool.title}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏ Редактировать",
                    callback_data=f"tool:edit:{tool.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"tool:delete:{tool.id}"
                )
            ]
        ]
    )

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "tools:create")
async def create_tool_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ToolForm.create_title)
    await callback.message.answer("Введите название типа товара:")
    await callback.answer()


@router.message(ToolForm.create_title)
async def create_tool_finish(message: Message, state: FSMContext):
    title = message.text.strip()

    exists = await ToolRepository.get_by_variable(title=title)
    if exists:
        await message.answer("❌ Такой тип уже существует")
        return

    await ToolRepository.add_record(title=title)

    await message.answer("✅ Тип товара создан")
    await state.clear()


@router.callback_query(F.data.startswith("tool:edit:"))
async def edit_tool_start(callback: CallbackQuery, state: FSMContext):
    tool_id = int(callback.data.split(":")[2])

    await state.update_data(edit_tool_id=tool_id)
    await state.set_state(ToolForm.edit_title)

    await callback.message.answer("Введите новое название типа товара:")
    await callback.answer()

@router.callback_query(F.data.startswith("tool:edit:"))
async def edit_tool_start(callback: CallbackQuery, state: FSMContext):
    tool_id = int(callback.data.split(":")[2])

    await state.update_data(edit_tool_id=tool_id)
    await state.set_state(ToolForm.edit_title)

    await callback.message.answer("Введите новое название типа товара:")
    await callback.answer()


@router.callback_query(F.data.startswith("tool:delete:"))
async def confirm_delete_tool(callback: CallbackQuery):
    tool_id = int(callback.data.split(":")[2])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data=f"tool:delete_confirm:{tool_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="tool:delete_cancel"
                )
            ]
        ]
    )

    await callback.message.answer("Удалить тип товара?", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("tool:delete_confirm:"))
async def delete_tool(callback: CallbackQuery):
    tool_id = int(callback.data.split(":")[2])

    reports = await ReportRepository.get_all_by_variable(tool_id=tool_id)

    if reports:
        await callback.answer(
            "Нельзя удалить — есть отчеты с этим типом",
            show_alert=True
        )
        return

    await ToolRepository.delete_by_id(tool_id)

    await callback.message.answer("❌ Тип товара удален")
    await callback.answer()


@router.callback_query(F.data == "tool:delete_cancel")
async def cancel_delete_tool(callback: CallbackQuery):
    await callback.message.answer("Удаление отменено")
    await callback.answer()


##############################

@router.message(F.text == "Техники", RoleFilter(["moderator"]))
async def vehicles_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Список", callback_data="vehicles:list")],
            [InlineKeyboardButton(text="➕ Добавить", callback_data="vehicles:create")]
        ]
    )
    await message.answer("Управление техникой:", reply_markup=keyboard)


@router.callback_query(F.data == "vehicles:list")
async def list_vehicles(callback: CallbackQuery):
    vehicles = await VehicleRepository.get_all()

    if not vehicles:
        await callback.message.answer("Техника не найдена")
        await callback.answer()
        return

    keyboard = []

    for vehicle in vehicles:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{vehicle.model} - {vehicle.number}",
                callback_data=f"vehicle:detail:{vehicle.id}"
            )
        ])

    await callback.message.answer(
        "📋 Список техники:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()

@router.callback_query(F.data.startswith("vehicle:detail:"))
async def vehicle_detail(callback: CallbackQuery):
    vehicle_id = int(callback.data.split(":")[2])
    vehicle = await VehicleRepository.get_by_id(vehicle_id)

    if not vehicle:
        await callback.answer("Не найдено", show_alert=True)
        return

    text = (
        f"🚗 Модель: {vehicle.model}\n"
        f"🔢 Номер: {vehicle.number}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏ Редактировать", callback_data=f"vehicle:edit:{vehicle.id}")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"vehicle:delete:{vehicle.id}")]
        ]
    )

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "vehicles:create")
async def create_vehicle_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VehicleForm.create_model)
    await callback.message.answer("Введите модель техники:")
    await callback.answer()


@router.message(VehicleForm.create_model)
async def create_vehicle_number(message: Message, state: FSMContext):
    await state.update_data(model=message.text.strip())
    await state.set_state(VehicleForm.create_number)
    await message.answer("Введите номер техники:")

@router.message(VehicleForm.create_number)
async def create_vehicle_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    number = message.text.strip()

    exists = await VehicleRepository.get_by_variable(number=number)
    if exists:
        await message.answer("❌ Такой номер уже существует")
        return

    await VehicleRepository.add_record(
        model=data["model"],
        number=number
    )

    await message.answer("✅ Техника добавлена")
    await state.clear()


@router.callback_query(F.data.startswith("vehicle:edit:"))
async def edit_vehicle_start(callback: CallbackQuery, state: FSMContext):
    vehicle_id = int(callback.data.split(":")[2])

    await state.update_data(edit_vehicle_id=vehicle_id)
    await state.set_state(VehicleForm.edit_model)

    await callback.message.answer("Введите новую модель:")
    await callback.answer()

@router.message(VehicleForm.edit_model)
async def edit_vehicle_number(message: Message, state: FSMContext):
    await state.update_data(model=message.text.strip())
    await state.set_state(VehicleForm.edit_number)
    await message.answer("Введите новый номер:")


@router.message(VehicleForm.edit_number)
async def edit_vehicle_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    number = message.text.strip()

    exists = await VehicleRepository.get_by_variable(number=number)

    if exists and exists.id != data["edit_vehicle_id"]:
        await message.answer("❌ Такой номер уже существует")
        return

    await VehicleRepository.update_record(
        id=data["edit_vehicle_id"],
        model=data["model"],
        number=number
    )

    await message.answer("✅ Техника обновлена")
    await state.clear()

@router.callback_query(F.data.startswith("vehicle:delete:"))
async def confirm_delete_vehicle(callback: CallbackQuery):
    vehicle_id = int(callback.data.split(":")[2])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data=f"vehicle:delete_confirm:{vehicle_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="vehicle:delete_cancel"
                )
            ]
        ]
    )

    await callback.message.answer("Удалить технику?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("vehicle:delete_confirm:"))
async def delete_vehicle(callback: CallbackQuery):
    vehicle_id = int(callback.data.split(":")[2])

    reports = await ReportRepository.get_all_by_variable(vehicle_id=vehicle_id)

    if reports:
        await callback.answer(
            "Нельзя удалить — есть отчеты с этой техникой",
            show_alert=True
        )
        return

    await VehicleRepository.delete_by_id(vehicle_id)

    await callback.message.answer("❌ Техника удалена")
    await callback.answer()


@router.callback_query(F.data == "vehicle:delete_cancel")
async def cancel_delete_vehicle(callback: CallbackQuery):
    await callback.message.answer("Удаление отменено")
    await callback.answer()


##############################

@router.message(F.text == "Пользователи", RoleFilter(["moderator"]))
async def users_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Список", callback_data="users:list")],
            [InlineKeyboardButton(text="➕ Добавить", callback_data="users:create")]
        ]
    )
    await message.answer("Управление пользователями:", reply_markup=keyboard)

@router.callback_query(F.data == "users:list")
async def list_users(callback: CallbackQuery):
    users = await UserRepository.get_all()

    if not users:
        await callback.message.answer("Пользователи не найдены")
        await callback.answer()
        return

    keyboard = []

    for user in users:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{user.fio}",
                callback_data=f"user:detail:{user.id}"
            )
        ])

    await callback.message.answer(
        "📋 Список пользователей:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("user:detail:"))
async def user_detail(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])
    user = await UserRepository.get_by_id(user_id)

    if not user:
        await callback.answer("Не найдено", show_alert=True)
        return

    role = await RoleRepository.get_by_id(user.role_id)

    text = (
        f"👤 ФИО: {user.fio}\n"
        f"🆔 TG ID: {user.tg_id}\n"
        f"🎭 Роль: {role.title}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏ Редактировать", callback_data=f"user:edit:{user.id}")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"user:delete:{user.id}")]
        ]
    )

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "users:create")
async def create_user_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserForm.create_fio)
    await callback.message.answer("Введите ФИО пользователя:")
    await callback.answer()


@router.message(UserForm.create_fio)
async def create_user_tg_id(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(UserForm.create_tg_id)
    await message.answer("Введите Telegram ID:")

@router.message(UserForm.create_tg_id)
async def create_user_role(message: Message, state: FSMContext):
    tg_id = message.text

    exists = await UserRepository.get_by_variable(tg_id=tg_id)
    if exists:
        await message.answer("❌ Такой Telegram ID уже существует")
        return

    await state.update_data(tg_id=tg_id)

    roles = await RoleRepository.get_all()

    keyboard = []
    for role in roles:
        if role.title != "admin":
            keyboard.append([
                InlineKeyboardButton(
                    text=role.title,
                    callback_data=f"user:create_role:{role.id}"
                )
            ])

    await state.set_state(UserForm.create_role)
    await message.answer(
        "Выберите роль:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data.startswith("user:create_role:"))
async def create_user_finish(callback: CallbackQuery, state: FSMContext):
    role_id = int(callback.data.split(":")[2])
    data = await state.get_data()

    await UserRepository.add_record(
        fio=data["fio"],
        tg_id=data["tg_id"],
        role_id=role_id
    )

    await callback.message.answer("✅ Пользователь создан")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("user:edit:"))
async def edit_user_start(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[2])

    await state.update_data(edit_user_id=user_id)
    await state.set_state(UserForm.edit_fio)

    await callback.message.answer("Введите новое ФИО:")
    await callback.answer()


@router.message(UserForm.edit_fio)
async def edit_user_tg_id(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(UserForm.edit_tg_id)
    await message.answer("Введите новый Telegram ID:")



@router.message(UserForm.edit_tg_id)
async def edit_user_role(message: Message, state: FSMContext):
    data = await state.get_data()

    exists = await UserRepository.get_by_variable(tg_id=message.text)
    if exists and exists.id != data["edit_user_id"]:
        await message.answer("❌ Такой Telegram ID уже существует")
        return

    await state.update_data(tg_id=message.text)

    roles = await RoleRepository.get_all()

    keyboard = []
    for role in roles:
        if role.title != "admin":
            keyboard.append([
                InlineKeyboardButton(
                    text=role.title,
                    callback_data=f"user:edit_role:{role.id}"
                )
            ])

    await state.set_state(UserForm.edit_role)
    await message.answer(
        "Выберите новую роль:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data.startswith("user:edit_role:"))
async def edit_user_finish(callback: CallbackQuery, state: FSMContext):
    role_id = int(callback.data.split(":")[2])
    data = await state.get_data()

    await UserRepository.update_record(
        id=data["edit_user_id"],
        fio=data["fio"],
        tg_id=data["tg_id"],
        role_id=role_id
    )

    await callback.message.answer("✅ Пользователь обновлен")
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("user:delete:"))
async def confirm_delete_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data=f"user:delete_confirm:{user_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="user:delete_cancel"
                )
            ]
        ]
    )

    await callback.message.answer("Удалить пользователя?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("user:delete_confirm:"))
async def delete_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])

    await UserRepository.delete_by_id(user_id)

    await callback.message.answer("❌ Пользователь удален")
    await callback.answer()

@router.callback_query(F.data == "user:delete_cancel")
async def cancel_delete_user(callback: CallbackQuery):
    await callback.message.answer("Удаление отменено")
    await callback.answer()
##############################


@router.message(F.text == "Получить отчет", RoleFilter(["moderator"]))
async def start(message: Message, state: FSMContext):

    keyboard = await get_moderator_report_keyboard()

    await message.answer("Выберите какой отчет Вам нужен", reply_markup=keyboard)
    await state.set_state(ReportForm.start)


@router.message(ReportForm.start)
async def selecting(message: Message, state: FSMContext):

    config = REPORT_TYPES.get(message.text)

    if not config:
        await message.answer("Выберите вариант из меню")
        return

    type_query, keyboard_func = config
    keyboard = await keyboard_func()

    await state.update_data(type=type_query)
    await state.set_state(ReportForm.finish)

    await message.answer("Выберите запись:", reply_markup=keyboard)


@router.message(ReportForm.finish)
async def finish(message: Message, state: FSMContext):

    data = await state.get_data()
    report_type = data.get("type")

    if not report_type:
        await message.answer("Ошибка состояния")
        return

    if report_type == "tool":
        entity = await ToolRepository.get_by_variable(title=message.text)
        filter_key = "tool_id"

    elif report_type == "user":
        entity = await UserRepository.get_by_variable(fio=message.text)
        filter_key = "user_id"

    elif report_type == "vehicle":
        name = message.text.split(" - ")[-1]
        entity = await VehicleRepository.get_by_variable(number=name)
        filter_key = "vehicle_id"

    else:
        await message.answer("Ошибка вида отчета")
        return

    if not entity:
        await message.answer("Запись не найдена")
        return

    await state.update_data(
        filter_key=filter_key,
        filter_value=entity.id
    )

    await send_reports_page(message, page=1, edit=False, **{filter_key: entity.id})


@router.callback_query(F.data.startswith("reports:"), ReportForm.finish)
async def paginate_reports(callback: CallbackQuery, state: FSMContext):

    page = int(callback.data.split(":")[1])
    data = await state.get_data()

    await send_reports_page(
        callback.message,
        page=page,
        edit=True,
        **{data["filter_key"]: data["filter_value"]}
    )

    await callback.answer()


@router.callback_query(F.data.startswith("report_detail:"), ReportForm.finish)
async def report_detail(callback: CallbackQuery):
    report_id = int(callback.data.split(":")[1])

    report = await ReportRepository.get_with_relations(report_id)

    if not report:
        await callback.answer("Отчет не найден", show_alert=True)
        return

    text = (
        f"📄 Отчет №{report.id}\n"
        f"👤 Пользователь: {report.user.fio}\n"
        f"🚗 Машина: {report.vehicle.number}\n"
        f"🛠 Тип: {report.tool.title}\n"
        f"📅 Дата: {report.created_at:%d.%m.%Y %H:%M}"
    )

    await callback.message.answer(text)

    for media in report.media:

        if not os.path.exists(media.file_url):
            await callback.message.answer(f"Файл не найден: {media.file_url}")
            continue

        file = FSInputFile(media.file_url)

        if media.file_type == "photo":
            await callback.message.answer_photo(file)

        elif media.file_type == "video":
            await callback.message.answer_video(file)

        elif media.file_type == "voice":
            await callback.message.answer_voice(file)

        elif media.file_type == "audio":
            await callback.message.answer_audio(file)

        elif media.file_type == "video_note":
            await callback.message.answer_video_note(file)
    await callback.answer()
