from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_functions_keyboard():
    """Функция для создания основной клавиатуры с кнопками действий."""
    keyboard = InlineKeyboardBuilder()
    # Создаем кнопки
    keyboard.add(InlineKeyboardButton(text='⁉️ Помощь и о боте', callback_data='help_and_about_bot'))
    keyboard.add(InlineKeyboardButton(text='ℹ️ Обо мне', callback_data='about_me'))
    keyboard.add(InlineKeyboardButton(text='🔊 Преобразовать текст в аудио',callback_data='text_to_audio'))
    keyboard.add(InlineKeyboardButton(text='🎙️ Конвертировать аудио в текст', callback_data='audio_to_text'))
    keyboard.add(InlineKeyboardButton(text='📄 Конвертировать PDF в DOC', callback_data='pdf_to_docs'))
    keyboard.add(InlineKeyboardButton(text='📂 Конвертировать в PDF', callback_data='docs_to_pdf'))
    keyboard.add(InlineKeyboardButton(text='🤖 Помощь от ИИ 🧠', callback_data='help_with_ai'))


    return keyboard.adjust(2, 1).as_markup()


