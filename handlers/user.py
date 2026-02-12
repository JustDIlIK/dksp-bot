from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from db.repositories.media import MediaRepository
from db.repositories.report import ReportRepository
from db.repositories.tool import ToolRepository
from db.repositories.user import UserRepository
from db.repositories.vehicle import VehicleRepository
from forms.user import Form
from keyboard.user import (
    get_tools_keyboard,
    get_vehicles_keyboard,
    get_main_keyboard, get_save_keyboard,
)

from middleware import RoleFilter

router = Router()


@router.message(F.text == "Отмена", RoleFilter(["user"]))
async def cancel_form(message: Message, state: FSMContext):

    keyboard = await get_main_keyboard()

    await state.clear()
    await message.answer("Отменил", reply_markup=keyboard)


@router.message(F.text == "Отправить данные", RoleFilter(["user"]))
async def start(message: Message, state: FSMContext):
    keyboard = await get_tools_keyboard()
    await message.answer("Выберите тип", reply_markup=keyboard)
    await state.set_state(Form.tool)


@router.message(Form.tool, F.text)
async def get_toll(message: Message, state: FSMContext):

    tool = await ToolRepository.get_by_id(int(message.text))

    if not tool:
        await message.answer("Выбрали несуществующий тип")
        return

    await state.update_data(tool_id=tool.id)
    keyboard = await get_vehicles_keyboard()
    await message.answer("Выберите технику", reply_markup=keyboard)
    await state.set_state(Form.vehicle)


@router.message(Form.vehicle, F.text)
async def get_vehicle(message: Message, state: FSMContext):

    vehicle = await VehicleRepository.get_by_variable(number=message.text.split(" - ")[-1])

    if not vehicle:
        await message.answer("Выбрали несуществующую технику")
        return

    keyboard = await get_save_keyboard()

    await state.update_data(vehicle_id=vehicle.id)
    await message.answer("Отправьте материалы (фото, видео)", reply_markup=keyboard)
    await state.set_state(Form.photo)


@router.message(Form.photo, F.photo | F.video | F.text | F.voice | F.audio | F.video_note)
async def get_vehicle(message: Message, state: FSMContext, bot: Bot):
    file_id = None
    file_name = None
    file_type = ""
    print("Accepted")
    data = await state.get_data()
    report_id = data.get("report_id", None)

    if message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name
        file_type = "video"
    elif message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_name = f"{photo.file_id}.jpg"
        file_type = "photo"
    elif message.voice:
        file = message.voice
        file_id = file.file_id
        file_name = f"{file.file_id}.ogg"
        file_type = "voice"
    elif message.audio:
        file = message.audio
        file_id = file.file_id
        file_name = file.file_name or f"{file.file_id}.mp3"
        file_type = "audio"
    elif message.video_note:
        file = message.video_note
        file_id = file.file_id
        file_name = f"{file.file_id}.mp4"
        file_type = "video_note"
    elif message.text and message.text == "Сохранить":
        await state.clear()
        keyboard = await get_main_keyboard()
        if not report_id:
            await message.answer("Вы ничего не отправили", reply_markup=keyboard)
        else:
            await ReportRepository.update_record(id=report_id, is_finished=True)
            await message.answer("Данные отправлены", reply_markup=keyboard)
        return
    if not file_id:
        await message.answer("Отправьте материалы (фото, видео)")

    user = await UserRepository.get_by_variable(tg_id=str(message.from_user.id))

    if not report_id:
        report = await ReportRepository.add_record(
            user_id=user.id, tool_id=data["tool_id"], vehicle_id=data["vehicle_id"]
        )
        print(f"{report=}")
        report_id = report.id
        await state.update_data(report_id=report.id)

    file = await bot.get_file(file_id)
    file_path = file.file_path
    local_path = f"downloads/{file_name}"

    await bot.download_file(file_path=file_path, destination=local_path)

    await MediaRepository.add_record(
        file_url=local_path,
        file_type=file_type,
        report_id=report_id,
    )
    await message.answer("✅")
