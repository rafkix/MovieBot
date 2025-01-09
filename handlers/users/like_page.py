import logging
from aiogram import Router
from aiogram.types import InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import bot
from data.config import CHANNEL_LINK
from database.database import async_session
from database.functions.movie import select_movie
from database.functions.save_movie import select_saved_movie, get_saved_movies, delete_saved_movie
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import menu

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def show_saved_movie(user_id: int, session: AsyncSession, page: int = 1):
    saved_movies = await get_saved_movies(user_id, session, page, page_size=1)

    if not saved_movies:
        # When no saved movies exist, show the "Bosh menu" button only
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🧧 Bosh menu", callback_data="main_menu"))
        return None, "❌ Siz hali kino saqlamadingiz.", builder.as_markup()

    builder = InlineKeyboardBuilder()
    movie = saved_movies[0]  # only get the first movie

    thumb = movie.thumb  # Assuming thumb is an attribute of the movie
    response_text = f"<b>🎬 Film nomi: {movie.movie_name}</b>\n"
    response_text += f"👁 Ko'rishlar: {movie.views}\n\n"
    builder.add(InlineKeyboardButton(text="📥 Kinoni yuklash", callback_data=f"download_{movie.movie_code}"))

    prev_button = InlineKeyboardButton(text="◀️ Oldingi", callback_data=f"prev_{page - 1}" if page > 1 else "page_1")
    next_button = InlineKeyboardButton(text="▶️ Keyingi",
                                       callback_data=f"next_{page + 1}" if len(saved_movies) == 1 else "disabled")

    builder.add(prev_button, next_button)
    builder.add(
        InlineKeyboardButton(text="🎞 Kinoni o'chirish", callback_data=f"my_delete_{movie.movie_code}"),
        InlineKeyboardButton(text="🧧 Bosh menu", callback_data="main_menu")  # Always show Bosh menu
    )
    builder.adjust(1, 2, 1)

    return thumb, response_text, builder.as_markup()


@router.callback_query(lambda c: c.data == 'saved_movies')
async def handle_saved_movies(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    async with async_session() as session:
        thumb, response_text, inline_buttons = await show_saved_movie(user_id, session, page=1)
        if thumb:
            media = InputMediaPhoto(media=thumb, caption=f"<b>{response_text}</b>")
            await callback_query.message.edit_media(media=media, reply_markup=inline_buttons)
        else:
            await callback_query.message.edit_text(text=response_text, reply_markup=inline_buttons)
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('next_') or c.data.startswith('prev_'))
async def handle_saved_movies_page(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    page_data = callback_query.data.split('_')[1]

    if page_data == 'disabled':
        await callback_query.answer()  # Yechik mavjud emas
        return

    page_change = int(page_data)
    page = max(page_change, 1)

    async with async_session() as session:
        thumb, response_text, inline_buttons = await show_saved_movie(user_id, session, page)

        if thumb:
            media = InputMediaPhoto(media=thumb, caption=response_text)
            await callback_query.message.edit_media(media=media, reply_markup=inline_buttons)
        else:
            await callback_query.answer("❌ Siz hali kino saqlamadingiz.",show_alert=True)

    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('download_'))
async def handle_movie_download(callback_query: CallbackQuery):
    movie_code = callback_query.data.split('_')[1]
    bot_info = await bot.get_me()

    async with async_session() as session:
        movie = await select_movie(movie_code, session)

        if movie:
            movie.views += 1
            session.add(movie)
            await session.commit()

            inline_buttons = InlineKeyboardBuilder()
            inline_buttons.add(
                InlineKeyboardButton(text="📤 Do'stlarga yuborish", switch_inline_query=f"{movie.movie_code}"),
                InlineKeyboardButton(text="💾 Saqlash", callback_data=f"save_{movie.movie_code}")
            )
            inline_buttons.add(
                InlineKeyboardButton(text="❌", callback_data=f"delete_{movie.movie_code}")
            )

            inline_buttons.adjust(2, 1)

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

            await callback_query.message.reply_video(
                video=movie.movie_url,
                caption=response,
                reply_markup=inline_buttons.as_markup()
            )
        else:
            await callback_query.message.answer("Bunday kodli kino mavjud emas!")

    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('my_delete_'))
async def handle_delete_saved_movie(callback_query: CallbackQuery):
    movie_code = callback_query.data.split('_')[2]
    user_id = callback_query.from_user.id

    async with async_session() as session:
        success = await delete_saved_movie(session=session, movie_code=movie_code, user_id=user_id)

        if success:
            await callback_query.answer("🎞 Kino muvaffaqiyatli o'chirildi.",show_alert=True)
            # Keyingi kinoga tahrir qilish
            thumb, response_text, inline_buttons = await show_saved_movie(user_id, session, page=1)
            if thumb:
                media = InputMediaPhoto(media=thumb, caption=f"<b>{response_text}</b>")
                await callback_query.message.edit_media(media=media, reply_markup=inline_buttons)
            else:
                await callback_query.message.edit_caption(caption=response_text, reply_markup=inline_buttons)
        else:
            await callback_query.message.answer("❌ Bunday kodli kino mavjud emas yoki o'chirib bo'lmadi.")
            # Agar kino mavjud bo'lmasa yoki o'chirilmasa, bosh menyuni ko'rsatish
            markup_start = await menu()
            await callback_query.message.edit_text(text="🧧 Bosh menyuga qayting.", reply_markup=markup_start)

    await callback_query.answer()
