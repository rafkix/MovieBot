import logging
from aiogram import Router, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils import markdown

from database.database import async_session  # Sessiya generatorini import qiling
from database.functions.users import add_user
from keyboards.inline import menu

router = Router()

# Logotip gif URL
bot_logo_url = "https://s6.ezgif.com/tmp/ezgif-6-dd4f55fb06.jpg"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def hello_bot(message: Message, command: CommandObject):
    user_info = message.from_user
    # Deep link parametrini olish
    payload = command.args
    referral = payload if payload else None

    # AsyncSession ni ishlatish
    async with async_session() as session:
        # Foydalanuvchini qo'shish
        await add_user(
            session=session,
            user_id=user_info.id,
            full_name=user_info.full_name or "No Name",
            lang=user_info.language_code or "en",
            referral=referral
        )

    # Menu yaratish
    markup_start = await menu()

    # Foydalanuvchiga xush kelibsiz xabarini yuborish
    await message.answer(
        text=f"""{markdown.hide_link(bot_logo_url)}<b>👋 Assalomu alaykum рафких, botimizga xush kelibsiz!

<i>🎥 Bot orqali siz sevimli filmlar, seriallar va multfilmlarni sifatli formatda ko'rishingiz mumkin.</i>

Quyidagi menudan kerakli bo'limni tanlang👇</b>""",
        reply_markup=markup_start  # Inline keyboard ni yuborish
    )

@router.callback_query(lambda c: c.data == 'main_menu')
async def handle_main_menu(callback_query: CallbackQuery, state: FSMContext):
    # The new text message to be sent
    text = f"""{markdown.hide_link(bot_logo_url)}<b>👋 Assalomu alaykum рафких, botimizga xush kelibsiz!  
    <i>🎥 Bot orqali siz sevimli filmlar, seriallar va multfilmlarni sifatli formatda ko'rishingiz mumkin.</i>  
    Quyidagi menudan kerakli bo'limni tanlang👇</b>"""

    # Prepare the markup for the menu
    markup_start = await menu()

    # Check if the current message is a media message or text
    if callback_query.message.text:
        # If the message has text, we can edit it
        await callback_query.message.edit_text(text=text, reply_markup=markup_start)
    else:
        # If the message has media, delete it first
        await callback_query.message.delete()

        # Send the new text message
        await callback_query.message.answer(text=text, reply_markup=markup_start)

    # Send a response to acknowledge the callback
    await callback_query.answer()

    # Clear the state
    await state.clear()

