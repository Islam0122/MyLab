from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from filter.chat_types import ChatTypeFilter
from keyboard.inline import *


start_functions_private_router = Router()
start_functions_private_router.message.filter(ChatTypeFilter(['private']))



async def send_welcome_message(user, target):
    """Функция для отправки приветственного сообщения с фото и кнопками."""
    photo_path = 'media/images/img.png'
    # Приветственное сообщение с дополнительным текстом
    welcome_message = (
        f"👋 Привет, {user.first_name}! Добро пожаловать в *Islam’s Lab*!\n\n"
        f"Здесь ты можешь использовать различные инструменты: перевод текста, скачивание видео, "
        f"общение с ИИ и много других полезных функций. Выбирай нужную опцию с помощью кнопок ниже и наслаждайся! 🚀"
    )
    # Отправка фото и приветственного сообщения с кнопками
    await target.answer_photo(
        photo=types.FSInputFile(photo_path),
        caption=welcome_message,
        reply_markup=start_functions_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


@start_functions_private_router.message(CommandStart())
@start_functions_private_router.message(F.text.lower() == 'start')
async def start_cmd(message: types.Message):
    """Обработчик команды /start"""
    await send_welcome_message(message.from_user, message)


@start_functions_private_router.callback_query(F.data.startswith('start_'))
async def start_command_callback_query(query: types.CallbackQuery) -> None:
    """Обработчик callback_query с командой start"""
    await query.message.delete()
    await send_welcome_message(query.from_user, query.message)


@start_functions_private_router.callback_query(F.data.startswith('return'))
async def return_command_callback_query(query: types.CallbackQuery) -> None:
    """Обработчик callback_query с командой return"""
    await send_welcome_message(query.from_user, query.message)


@start_functions_private_router.callback_query(F.data.startswith('help_and_about_bot'))
async def help_and_about_bot_command_callback_query(query: types.CallbackQuery) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='🔙 Вернуться в главное меню', callback_data='start_'))
    await query.message.edit_caption(
        caption=(
            "ℹ️ *Информация о боте:*\n\n"
            "Добро пожаловать в *Islam’s Lab*! 🚀\n\n"
            "Это место для экспериментов и полезных инструментов. В нем ты найдешь различные функции, "
            "такие как:\n"
            "🎥 Скачивание видео с YouTube\n"
            "💬 Перевод текста\n"
            "🤖 Общение с ИИ\n"
            "🎙️ Преобразование аудио в текст\n"
            "📄 Преобразование PDF в DOC и наоборот\n\n"
            "Все эти функции доступны прямо здесь, в главном меню. Используй кнопки ниже, чтобы начать!"
        ),
        reply_markup=keyboard.adjust(1).as_markup(),
        parse_mode=ParseMode.MARKDOWN,
    )


@start_functions_private_router.callback_query(F.data.startswith('about_me'))
async def about_me_command_callback_query(query: types.CallbackQuery) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='🔙 Вернуться в главное меню', callback_data='start_'))
    keyboard.add(InlineKeyboardButton(text='📄 Посмотреть моё резюме', callback_data='resume'))

    caption = (
        "ℹ️ *Обо мне*\n\n"
        "Привет! Меня зовут *Islam*, и я — начинающий разработчик. Мои увлечения связаны с программированием и технологиями, "
        "и я постоянно стремлюсь развивать свои навыки.\n\n"
        "В данный момент я изучаю:\n"
        "💻 Программирование на Python\n"
        "🌐 Веб-разработка с использованием Django и Flask\n"
        "📱 Начинаю осваивать JavaScript\n\n"
        "Я создаю различные инструменты и проекты, включая ботов, веб-приложения и другие интересные вещи. "
        "Этот бот — это результат моих экспериментов и разработки. Я всегда открыт к новым знаниям и стремлюсь совершенствоваться!\n\n"
        "Используй меню ниже, чтобы вернуться на главный экран!"
    )

    await query.message.edit_caption(
        caption=caption,
        reply_markup=keyboard.adjust(1).as_markup(),
        parse_mode=ParseMode.MARKDOWN,
    )


@start_functions_private_router.callback_query(F.data.startswith('resume'))
async def resume_command_callback_query(query: types.CallbackQuery) -> None:
    # Отправляем PDF-файл
    await query.message.answer_document(document=FSInputFile('media/new_islam_duishobaev.pdf',filename= 'media/new_islam_duishobaev.pdf'))