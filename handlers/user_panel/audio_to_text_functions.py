import asyncio
from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, FSInputFile
from handlers.user_panel.start_functions import send_welcome_message
from keyboard.inline import InlineKeyboardBuilder
from filter.chat_types import ChatTypeFilter
import os
import subprocess
import speech_recognition as sr

audio_to_text_private_router = Router()
audio_to_text_private_router.message.filter(ChatTypeFilter(['private']))
r = sr.Recognizer()


class AudioToTextState(StatesGroup):
    waiting_for_audio = State()
    waiting_for_caption = State()  # Для хранения идентификатора сообщения


@audio_to_text_private_router.callback_query(F.data == 'audio_to_text')
async def audio_to_text_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик вызова кнопки для преобразования аудио в текст."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_audio_to_text'))
    m = await query.message.edit_caption(
        caption="Пожалуйста, отправьте аудиосообщение, чтобы я мог преобразовать его в текст:",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(message_id=m.message_id)
    await state.set_state(AudioToTextState.waiting_for_audio)
    await query.answer()


@audio_to_text_private_router.callback_query(F.data == 'cancel_audio_to_text')
async def cancel_audio_to_text(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.delete()
    await query.answer("Процесс преобразования отменен.")
    await send_welcome_message(query.from_user, query.message)


@audio_to_text_private_router.message(AudioToTextState.waiting_for_audio)
async def audio_to_text_process(message: types.Message, state: FSMContext, bot: Bot) -> None:
    """Обрабатывает голосовые сообщения или аудиофайлы."""
    if message.voice:  # Если это голосовое сообщение
        await message.answer("Голосовое сообщение принято! Сейчас обработаем...")
        await state.clear()

    elif message.audio:  # Если это обычный аудиофайл
        await message.answer("Аудиофайл принят! Сейчас обработаем...")
        await state.clear()

    else:  # Если сообщение не содержит аудио
        await message.delete()
        m = await message.answer("❗ Пожалуйста, отправьте аудиосообщение или аудиофайл.")
        await asyncio.sleep(5)
        await m.delete()


