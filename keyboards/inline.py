from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import config


# Menyu yaratish funktsiyasi
async def menu():
    builder = InlineKeyboardBuilder()

    # Tugmalarni qo'shish
    builder.add(
        InlineKeyboardButton(text="🎬 Film qidirish", callback_data="search_movie"),
        InlineKeyboardButton(text="⭐ Top filimlar", callback_data="top_movies"),
        InlineKeyboardButton(text="🎲 Random film", callback_data="random_movie"),
        InlineKeyboardButton(text="💾 Saqlanganlar", callback_data="saved_movies"),
        InlineKeyboardButton(text="🎥 Janrlar", callback_data="search_by_genre"),
        InlineKeyboardButton(text="🔍 Kinoni nomi orqali qidirish", switch_inline_query=""),
    )
    builder.adjust(2,2,1,1)

    return builder.as_markup()

async def admin_panels():
    builder = InlineKeyboardBuilder()

    # Tugmalarni qo'shish
    builder.add(
        InlineKeyboardButton(text="📋 Kanallar", callback_data="view_channels"),
        InlineKeyboardButton(text="🎬 Kino qo'shish", callback_data="start_add_movie"),
        InlineKeyboardButton(text="👥 Foydalanuvchilar soni", callback_data="view_users_count"),
        InlineKeyboardButton(text="📨 Xabar yuborish", callback_data="send_message"),
        InlineKeyboardButton(text="✅ Hammani qo'shish", callback_data="approve_all"),
    )

    # Tugmalarni tartibga solish
    builder.adjust(2)  # Har bir qatorda 1 ta tugma
    return builder.as_markup()

# Channel yaratish funksiyasi
async def admin_channel():
    builder = InlineKeyboardBuilder()

    # Tugmalarni bir marta chaqiruvda qo'shish
    builder.add(
        InlineKeyboardButton(text="📋 Barcha kanallarni ko'rish", callback_data="list_channels"),
        InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel"),
        InlineKeyboardButton(text="❌ Kanalni o'chirish", callback_data="delete_channel"),
        InlineKeyboardButton(text="📊 Kanallar soni", callback_data="count_channels"),
        InlineKeyboardButton(text="⬅️ Ortga", callback_data='admin')
    )

    # Tugmalarni tartibga keltirish (2 ta har bir qatorda)
    builder.adjust(2)

    return builder.as_markup()
