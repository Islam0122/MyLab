import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv

from handlers.user_panel.PDF_to_docs_functions import PDF_to_docs_private_router
from handlers.user_panel.audio_to_text_functions import audio_to_text_private_router
from handlers.user_panel.docs_to_pdf_functions import docs_to_pdf_private_router
from handlers.user_panel.help_with_aii_functions import ai_help_private_router
from handlers.user_panel.start_functions import start_functions_private_router
from handlers.user_panel.text_to_audio_functions import text_to_audio_private_router

load_dotenv(find_dotenv())

from common.bot_cmds_list import private

bot = Bot(token=os.getenv('TOKEN'))
bot.my_admins_list = [5627082052, ]
bot.group_id = os.getenv('group_id')

dp = Dispatcher()

dp.include_router(start_functions_private_router)
dp.include_router(text_to_audio_private_router)
dp.include_router(PDF_to_docs_private_router)
dp.include_router(audio_to_text_private_router)
dp.include_router(docs_to_pdf_private_router)
dp.include_router(ai_help_private_router)

async def on_startup(bot):
    await bot.send_message(bot.my_admins_list[0], "Сервер успешно запущен! 😊 Привет, босс!")


async def on_shutdown(bot):
    await bot.send_message(bot.my_admins_list[0], "Сервер остановлен. 😔 Проверьте его состояние, босс!")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
