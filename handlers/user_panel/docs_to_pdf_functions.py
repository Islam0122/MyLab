from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, FSInputFile
import asyncio
from handlers.user_panel.start_functions import send_welcome_message
from keyboard.inline import InlineKeyboardBuilder
from filter.chat_types import ChatTypeFilter
from aiogram import Bot, types


docs_to_pdf_private_router = Router()
docs_to_pdf_private_router.message.filter(ChatTypeFilter(['private']))


class docs_to_pdf_State(StatesGroup):
    waiting_for_doc_file = State()
    processing_file = State()


@docs_to_pdf_private_router.callback_query(F.data == 'docs_to_pdf')
async def docs_to_pdf_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_docs_to_pdf'))
    m = await query.message.edit_caption(
        caption=(
            "📄 Пожалуйста, отправьте документ (DOC, DOCX, TXT и т.д.), который нужно преобразовать в PDF. "
            "Размер файла не должен превышать 10 МБ. "
            "Если передумали, нажмите ❌ Отмена."
        ),
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(message_id=m.message_id)
    await query.answer("Ожидаю документ для конвертации.")
    await state.set_state(docs_to_pdf_State.waiting_for_doc_file)


@docs_to_pdf_private_router.callback_query(F.data == 'cancel_docs_to_pdf')
async def cancel_docs_to_pdf(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.delete()
    await query.answer("Действие отменено.")
    await send_welcome_message(query.from_user, query.message)  # Здесь добавьте вашу функцию приветствия


@docs_to_pdf_private_router.message(docs_to_pdf_State.waiting_for_doc_file)
async def docs_to_pdf_process(message: types.Message, state: FSMContext, bot: Bot) -> None:
    if message.document:
        # Проверка формата файла
        file_extension = message.document.file_name.split('.')[-1].lower()
        if file_extension in ["doc", "docx", "txt"]:
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
            m = await message.answer("Неверный формат файла. Пожалуйста, отправьте файл формата DOC, DOCX или TXT.")
            await asyncio.sleep(5)
            await m.delete()
    else:
        await message.delete()
        m = await message.answer("Пожалуйста, отправьте документ в формате DOC, DOCX или TXT.")
        await asyncio.sleep(5)
        await m.delete()