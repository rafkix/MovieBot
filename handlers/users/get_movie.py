import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils import markdown

from app import bot
from data.config import CHANNEL_LINK
from database.database import async_session
from database.functions.movie import select_movie
from database.functions.save_movie import select_saved_movie, save_movie_to_db

# Router obyekti
router = Router()

# FSM uchun state (holat)lar
class MovieSearch(StatesGroup):
    waiting_for_code = State()

# Film kodini kiritishni so'rash uchun callback handler
@router.callback_query(lambda c: c.data == 'search_movie')
async def search_movie(callback_query: CallbackQuery, state: FSMContext):
    url = "https://s6.ezgif.com/tmp/ezgif-6-dd4f55fb06.jpg"

    # Inline tugmalar yaratish
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Ortga", callback_data="main_menu")
            ]
        ]
    )

    # Rasm va caption bilan birga inline tugmalarni yuborish
    await callback_query.message.edit_text(
        text=f"{markdown.hide_link(url)}<b>🔍 Film kodini kiriting:</b>\n\n<i>‼️Eslatma: Film kodlarini @ kanalidan olishingiz mumkin!</i>",
        reply_markup=inline_buttons
    )
    await state.set_state(MovieSearch.waiting_for_code)

# Foydalanuvchi kiritgan film kodini qayta ishlash
@router.message(F.content_type == 'text', MovieSearch.waiting_for_code)
async def handle_movie_code(message: Message, state: FSMContext):
    movie_code = message.text  # Xabar matnidan kino kodini olish
    bot_info = await bot.get_me()

    # Kino kodining raqam ekanligini tekshirish
    if not movie_code.isdigit():
        await message.answer("❌ Iltimos, faqat raqamli kino kodini kiriting.")
        return

    async with async_session() as session:
        try:
            # Kino kodiga qarab filmni ma'lumotlar bazasidan olish
            movie = await select_movie(movie_code, session)

            if movie:
                # Ko'rishlar sonini oshirish va ma'lumotlarni saqlash
                movie.views += 1
                session.add(movie)
                await session.commit()

                # Inline tugmalar: Ulashish va O'chirish
                inline_buttons = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="📤 Do'stlarga yuborish", switch_inline_query=f"{movie.movie_code}"),
                            InlineKeyboardButton(text="💾 Saqlash", callback_data=f"save_{movie.movie_code}")
                        ],
                        [
                            InlineKeyboardButton(text="❌", callback_data=f"delete_{movie.movie_code}")
                        ]
                    ]
                )

                response = (
                    f"<b>🎬 Nomi: {movie.movie_name}</b>\n\n"
                    f"➖➖➖➖➖➖➖\n\n"
                    f"<b>🌐 Davlati: {movie.country}\n</b>"
                    f"<b>🚩 Tili: {movie.movie_lang}\n</b>"
                    f"<b>🎭 Janri: #{movie.genre}\n</b>"
                    f"<b>💿 Sifati: {movie.quality}\n</b>"
                    f"<b>📆 Yili: {movie.year}\n</b>"
                    f"<b>🔢 Film kodi: <code>{movie.movie_code}\n</code></b>"
                    f"<b>👁 Ko'rishlar: {movie.views}\n\n</b>"
                    f"<b>👇👇👇👇👇👇👇👇\n</b>"
                    f"<b><a href='https://t.me/{bot_info.username}?start=movie_{movie.movie_code}'>TOMOSHA QILISH UCHUN BOSING</a></b>\n"
                    f"<b>👆👆👆👆👆👆👆👆\n\n</b>"
                    f"<b>🍿 Filmlar olami: @{CHANNEL_LINK}\n</b>"
                    f"<b>🤖 Eng Ajoyib Filmlar: @{bot_info.username}</b>"
                )

                # Video va tafsilotlar bilan javob berish
                await message.reply_video(
                    video=movie.movie_url,
                    title=f"{movie.movie_name}",
                    thumb=movie.thumb,
                    caption=response,
                    reply_markup=inline_buttons
                )
            else:
                await message.answer("Bunday kodli kino mavjud emas!")
        except Exception as e:
            await message.answer("❌ Kino topishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

    await state.clear()  # Holatni qayta tiklash

# Foydalanuvchi filmni saqlaganda callback handler
@router.callback_query(lambda c: c.data.startswith("save_"))
async def save_movie_handler(callback_query: CallbackQuery):
    movie_code = callback_query.data.split("_")[1]  # Callback ma'lumotidan kino kodini olish
    user_id = callback_query.from_user.id  # Foydalanuvchi ID sini olish

    async with async_session() as session:
        try:
            # Kino kodiga qarab filmni ma'lumotlar bazasidan olish
            movie = await select_movie(movie_code, session)

            if movie:
                # Foydalanuvchi filmni allaqachon saqlaganligini tekshirish
                existing_movie = await select_saved_movie(movie_code, user_id, session)
                if existing_movie:
                    await callback_query.answer(f"❌ Siz bu filmi allaqachon saqlagansiz!")
                    return

                # Filmni foydalanuvchi uchun saqlash
                await save_movie_to_db(
                    session=session,
                    user_id=user_id,
                    movie_code=movie.movie_code,
                    movie_name=movie.movie_name,
                    thumb=movie.thumb,
                    views=movie.views,
                )

                await callback_query.answer(f"🎬 {movie.movie_name} saqlandi!")
            else:
                await callback_query.answer("❌ Kino topilmadi!")
        except Exception as e:
            await callback_query.answer("❌ Kino saqlashda xatolik yuz berdi.")

# Foydalanuvchi filmni o'chirganda callback handler
@router.callback_query(F.data.startswith("delete_"))
async def delete_movie_handler(query: CallbackQuery):
    movie_code = query.data.split("_")[1]  # Callback ma'lumotidan kino kodini olish
    await query.message.delete()  # Xabarni o'chirish

    try:
        await query.answer("❌ Kino o'chirildi!")
    except Exception as e:
        await query.answer("❌ Kino o'chirishda xatolik yuz berdi.")
