import asyncio
from aiogram import Bot, Dispatcher, Router


from config import settings
from handlers.user import router as user_router
from handlers.common import router as common_user
from handlers.moderator import router as moderator_user

from middleware import AuthMiddleware

dp = Dispatcher()
dp.include_router(common_user)
dp.include_router(user_router)
dp.include_router(moderator_user)

dp.message.outer_middleware(AuthMiddleware())

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    print("Starting")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())