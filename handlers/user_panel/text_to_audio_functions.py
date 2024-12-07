import asyncio

from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, FSInputFile
from gtts import gTTS
import os
from handlers.user_panel.start_functions import send_welcome_message
from keyboard.inline import InlineKeyboardBuilder
from filter.chat_types import ChatTypeFilter

text_to_audio_private_router = Router()
text_to_audio_private_router.message.filter(ChatTypeFilter(['private']))


class TextToAudioState(StatesGroup):
    waiting_for_text = State()
    waiting_for_caption = State()  # Для хранения идентификатора сообщения


@text_to_audio_private_router.callback_query(F.data == 'text_to_audio')
async def text_to_audio_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик вызова кнопки для преобразования текста в аудио."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_text_to_audio'))

    # Сохраняем информацию о текущем сообщении, чтобы позже удалить его
    m = await query.message.edit_caption(
        caption="🔊 Преобразование текста в аудио...\n\nВведите текст, который хотите преобразовать:",
        reply_markup=keyboard.as_markup()
    )

    # Сохраняем идентификатор сообщения в состояние
    await state.update_data(message_id=m.message_id)

    await query.answer("Введите текст, который нужно преобразовать в аудио:")
    await state.set_state(TextToAudioState.waiting_for_text)


@text_to_audio_private_router.callback_query(F.data == 'cancel_text_to_audio')
async def cancel_text_to_audio(query: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик отмены операции преобразования текста в аудио."""
    await state.clear()
    await query.message.delete()
    await query.answer("🔊 Операция преобразования текста в аудио была отменена.")
    await send_welcome_message(query.from_user, query.message)


@text_to_audio_private_router.message(TextToAudioState.waiting_for_text)
async def text_to_audio_process(message: types.Message, state: FSMContext, bot: Bot) -> None:
    if message.text :
        """Обработчик текста для преобразования в аудио."""
        text = message.text
        tts = gTTS(text=text, lang='ru')

        # Сохраняем аудиофайл
        file_path = f"hello.mp3"
        tts.save(file_path)
        voice = FSInputFile(file_path)

        # Отправляем голосовое сообщение
        await message.answer_voice(voice)

        # Удаляем временный аудиофайл
        os.remove(file_path)

        # Получаем информацию о сообщении для удаления
        user_data = await state.get_data()
        message_id = user_data.get("message_id")

        if message_id:
            # Удаляем сообщение, которое мы редактировали ранее
            await bot.delete_message(message.chat.id, message_id)

        # Удаляем исходное текстовое сообщение пользователя
        await message.delete()


        # Отправляем приветственное сообщение
        await send_welcome_message(message.from_user, message)
        await state.clear()

    else:
        await message.delete()
        m = await message.answer("Пожалуйста, отправьте текст.")
        await asyncio.sleep(5)
        await m.delete()


