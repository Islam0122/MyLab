import asyncio

from aiogram import F, Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.ai_function import sent_prompt_and_get_response
from handlers.user_panel.start_functions import send_welcome_message
from keyboard.inline import start_functions_keyboard


ai_help_private_router = Router()
ai_help_private_router.message.filter(ChatTypeFilter(['private']))


class AiAssistanceState(StatesGroup):
    WaitingForQuestion = State()


@ai_help_private_router.callback_query(F.data.startswith("help_with_ai"))
@ai_help_private_router.callback_query(F.data.startswith("help_with_ai_start"))
async def help_with_ai_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_help_with_ai'))
    m = await query.message.edit_caption(
        caption="Задайте свой вопрос, и ИИ постарается помочь вам. 🧠💡",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(message_id=m.message_id)
    await query.answer("Ждем ваш вопрос! 📝")
    await state.set_state(AiAssistanceState.WaitingForQuestion)


@ai_help_private_router.callback_query(F.data.startswith("cancel_help_with_ai"))
async def cancel_help_with_ai_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.delete()
    await query.answer("Помощь отменена. Если хотите, можете задать новый вопрос.")
    await send_welcome_message(query.from_user, query.message)


@ai_help_private_router.message(AiAssistanceState.WaitingForQuestion)
async def process_help_request(message: types.Message, state: FSMContext, bot: Bot):
    # Формируем имя пользователя
    user_info = message.from_user.first_name or ""
    if message.from_user.last_name:
        user_info += f" {message.from_user.last_name}"
    if message.from_user.username:
        user_info += f" (@{message.from_user.username})"

    if message.text:
        # Отправляем сообщение с подтверждением и сохраняем его
        processing_message = await message.answer(f"Запрос принят, {user_info}!\n💭 Ещё чуть-чуть, готовлю ответ...")

        # Генерируем ответ с ИИ
        generated_help = sent_prompt_and_get_response(message.text)
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='↩️ Вернуться', callback_data='return'))
        await bot.edit_message_text(
            chat_id=processing_message.chat.id,
            message_id=processing_message.message_id,
            text=generated_help,
            reply_markup=keyboard.as_markup()
        )
        user_data = await state.get_data()
        message_id = user_data.get("message_id")

        if message_id:
            # Удаляем сообщение, которое мы редактировали ранее
            await bot.delete_message(message.chat.id, message_id)

        await state.clear()

    else:
        # Если сообщение пустое, удаляем его и отправляем новое сообщение
        await message.delete()
        m = await message.answer("Пожалуйста, задайте свой вопрос.")
        await asyncio.sleep(5)
        await m.delete()


