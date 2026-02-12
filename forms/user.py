from aiogram.fsm.state import StatesGroup, State



class Form(StatesGroup):
    tool = State()
    vehicle = State()
    photo = State()
    finish = State()