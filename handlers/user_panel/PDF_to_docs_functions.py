from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, FSInputFile
import asyncio
import os
import PyPDF2
from docx import Document
from handlers.user_panel.start_functions import send_welcome_message
from keyboard.inline import InlineKeyboardBuilder
from filter.chat_types import ChatTypeFilter
from aiogram import Bot, types
from aiogram.types import InputFile
from pdf2docx import Converter
import os

PDF_to_docs_private_router = Router()
PDF_to_docs_private_router.message.filter(ChatTypeFilter(['private']))


class PDF_to_docs_State(StatesGroup):
    waiting_for_pdf_file = State()
    waiting_for_caption = State()


def convert_pdf_to_word(pdf_path, word_path):
    cv = Converter(pdf_path)
    cv.convert(word_path)
    cv.close()


@PDF_to_docs_private_router.callback_query(F.data == 'pdf_to_docs')
async def pdf_to_docs_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_pdf_to_docs'))
    m = await query.message.edit_caption(
        caption="📄 Отправьте PDF-файл, который хотите преобразовать в документ. Размер файла не должен превышать 10 МБ.",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(message_id=m.message_id)
    await query.answer("Отправьте PDF-файл.")
    await state.set_state(PDF_to_docs_State.waiting_for_pdf_file)


@PDF_to_docs_private_router.callback_query(F.data == 'cancel_pdf_to_docs')
async def cancel_pdf_to_docs(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.delete()
    await query.answer("Действие отменено.")
    await send_welcome_message(query.from_user, query.message)


@PDF_to_docs_private_router.message(PDF_to_docs_State.waiting_for_pdf_file)
async def pdf_to_docs_process(message: types.Message, state: FSMContext, bot: Bot) -> None:
    if message.document:
        if message.document.mime_type == "application/pdf":
            document = message.document
            pdf_path = f"downloads/{document.file_name}"
            word_path = pdf_path.replace(".pdf", ".docx")
            os.makedirs("downloads", exist_ok=True)

            # Загружаем файл через Bot
            try:
                await bot.download(document.file_id, destination=pdf_path)
            except Exception as e:
                await message.answer(f"❌ Ошибка при загрузке файла: {e}")
                return

            # Конвертируем PDF в Word
            try:
                convert_pdf_to_word(pdf_path, word_path)
                await message.reply_document(FSInputFile(word_path), caption="Вот ваш Word-документ!")
            except Exception as e:
                await message.reply(f"❌ Произошла ошибка при конвертации: {e}")
            finally:
                # Удаляем временные файлы
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                if os.path.exists(word_path):
                    os.remove(word_path)
                user_data = await state.get_data()
                message_id = user_data.get("message_id")

                if message_id:
                    # Удаляем сообщение, которое мы редактировали ранее
                    await bot.delete_message(message.chat.id, message_id)

                # Удаляем исходное текстовое сообщение пользователя
                await message.delete()
                await state.clear()
                await send_welcome_message(message.from_user, message)
        else:
            await message.delete()
            m = await message.answer("❌ Отправленный файл не является PDF."
                                     "Пожалуйста, отправьте корректный файл.")
            await asyncio.sleep(6)
            await m.delete()
    else:
        await message.delete()
        m = await message.answer("❌ Пожалуйста, отправьте PDF-файл.")
        await asyncio.sleep(5)
        await m.delete()

