import logging

from aiogram.filters import Command

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from data.config import ADMIN_ID
from database.database import async_session
from database.functions.channel import all_channels
from database.functions.channel_join import get_all_pending_requests, delete_all_requests
from database.functions.users import count_user
from filters.is_admin import IsAdmin
from keyboards.inline import admin_panels, admin_channel

router = Router()



@router.message(Command("admin"), IsAdmin(ADMIN_ID))
async def admin_panel_handler(message: Message):
    text = "〽️ Siz admin paneldasiz kerakli menu tanlang:"
    reply_markup = await admin_panels()
    await message.answer(text=text, reply_markup=reply_markup)


@router.callback_query(lambda c: c.data == "admin", IsAdmin(ADMIN_ID))
async def admin_panel_handler(query: CallbackQuery):
    text = "🔙 Asosiy menyuga qaytdingiz. Tanlang:"
    reply_markup = await admin_panels()

    await query.message.edit_text(text=text, reply_markup=reply_markup)


# 1. **Kanallarni ko'rsatish handleri**
@router.callback_query(lambda c: c.data == "view_channels", IsAdmin(ADMIN_ID))
async def view_channels_handler(callback: CallbackQuery):
    async with async_session() as session:
        channels = await all_channels(session)  # Barcha kanallarni olish
        if channels:
            text = "<b>📋 Kanallar ro'yxati:</b>\n\n"
            for index, channel in enumerate(channels, start=1):
                text += f"{index}. {channel.channel_link}\n"
        else:
            text = "📋 Kanallar mavjud emas."
    await callback.message.edit_text(text, reply_markup=await admin_channel(), disable_web_page_preview=True)


@router.callback_query(lambda c: c.data == "view_users_count", IsAdmin(ADMIN_ID))
async def view_users_count_handler(callback: CallbackQuery):
    async with async_session() as session:
        user_count = await count_user(session)  # Foydalanuvchilar sonini hisoblash
        text = f"<b>👥 Foydalanuvchilar soni:</b> {user_count}"
    await callback.message.edit_text(text, reply_markup=await admin_panels())

# Admin "Tasdiqlash" tugmasini bosganda barcha foydalanuvchilarni qo'shish
@router.callback_query(F.data == "approve_all")
async def approve_all_requests(callback: CallbackQuery):
    chat = callback.message.chat

    async with async_session() as session:
        # Bazadan barcha so'rovlarni olish
        pending_requests = await get_all_pending_requests(session=session, channel_id=chat.id)

        # Barcha so'rovlarni ko'rib chiqish
        for request in pending_requests:
            try:
                # Kanalga qo'shishni tasdiqlash
                await callback.bot.approve_chat_join_request(
                    chat_id=chat.id,
                    user_id=request.user_id
                )
            except Exception as e:
                logging.error(f"Foydalanuvchini qo'shishda xatolik: {e}")

        # Bazani tozalash
        await delete_all_requests(session=session, channel_id=chat.id)

    await callback.message.edit_text("✅ Barcha foydalanuvchilar qo'shildi!")