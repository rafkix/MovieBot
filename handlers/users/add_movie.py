import random
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils import markdown
from sqlalchemy.util import await_only

from data.config import ADMIN_ID, CHANNEL_LINK_SEND, CHANNEL_LINK
from database.database import async_session
from database.functions.movie import add_movie
from keyboards.inline import admin_panels
from states import AddMovieState
from app import bot
import logging

router = Router()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Starting the process of movie addition
@router.callback_query(F.data == "start_add_movie")
async def start_movie_addition(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        text="📋 Iltimos kinoni yuboring:"
    )
    await state.set_state(AddMovieState.waiting_for_video_url)
    await callback_query.answer()

# Handling video post
@router.message(AddMovieState.waiting_for_video_url, F.content_type == "video")
async def handle_video_post(message: Message, state: FSMContext):
    video = message.video.file_id
    sent_message = await bot.send_video(
        chat_id=f"@{CHANNEL_LINK_SEND}", video=video
    )
    video_url = f"https://t.me/{CHANNEL_LINK_SEND}/{sent_message.message_id}"
    await message.answer(
        text=f"🔔 Video yuborildi.\nURL: {video_url}\n📋 Iltimos, kinoning nomini kiriting:"
    )
    await state.update_data(video_url=video_url)
    await state.set_state(AddMovieState.waiting_for_name)

# Getting movie name
@router.message(AddMovieState.waiting_for_name)
async def get_movie_name(message: Message, state: FSMContext):
    movie_name = message.text
    await state.update_data(movie_name=movie_name)
    await state.set_state(AddMovieState.waiting_for_lang)
    await message.answer("📖 Iltimos, kinoning tilini kiriting:")

@router.message(AddMovieState.waiting_for_lang)
async def get_movie_lang(message: Message, state: FSMContext):
    movie_lang = message.text
    await state.update_data(movie_lang=movie_lang)
    await message.answer("📸 Iltimos, kinoning rasmni yuboring:")
    await state.set_state(AddMovieState.waiting_for_thumbnail)

# Getting movie thumbnail
@router.message(AddMovieState.waiting_for_thumbnail, F.content_type == "photo")
async def get_movie_thumbnail(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data(thumbnail=photo)
    await message.answer("🔔 Rasm qabul qilindi. Iltimos, kinoning davlatini kiriting:")
    await state.set_state(AddMovieState.waiting_for_country)

# Getting country
@router.message(AddMovieState.waiting_for_country)
async def get_movie_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await state.set_state(AddMovieState.waiting_for_genre)
    await message.answer("🎬 Iltimos, kinoning janrlarini kiriting (vergul bilan ajrating, masalan: Sarguzasht, Drama):")

# Getting genre
@router.message(AddMovieState.waiting_for_genre)
async def get_movie_genre(message: Message, state: FSMContext):
    genres = [genre.strip() for genre in message.text.split(",")]  # Create a list of genres
    await state.update_data(genre=genres)
    await state.set_state(AddMovieState.waiting_for_quality)
    await message.answer("⚡ Iltimos, kinoning sifatini kiriting (masalan: 1080p, 4K):")

# Getting quality
@router.message(AddMovieState.waiting_for_quality)
async def get_movie_quality(message: Message, state: FSMContext):
    await state.update_data(quality=message.text)
    await state.set_state(AddMovieState.waiting_for_year)
    await message.answer("📅 Iltimos, kinoning chiqarilgan yilini kiriting (masalan: 2024):")

# Getting year
@router.message(AddMovieState.waiting_for_year)
async def get_movie_year(message: Message, state: FSMContext):
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await state.set_state(AddMovieState.waiting_for_description)
        await message.answer("📝 Iltimos, kinoning tavsifini kiriting:")
    except ValueError:
        await message.answer("❌ Iltimos, yilni to'g'ri formatda kiriting.")

# Getting description
@router.message(AddMovieState.waiting_for_description)
async def get_movie_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("🔔 Ma'lumotlar saqlanmoqda...")
    await save_movie_info(message, state)
    await state.set_state(AddMovieState.waiting_for_video_url)  # Reset the state for the next movie

# Saving movie information to the database
async def save_movie_info(message: Message, state: FSMContext):
    bot_info = await bot.get_me()
    data = await state.get_data()
    video_url = data['video_url']
    movie_name = data['movie_name']
    movie_lang = data['movie_lang']
    thumb = data['thumbnail']
    country = data['country']
    genres = ", ".join(data['genre'])  # Convert the list of genres to a comma-separated string
    quality = data['quality']
    year = data['year']
    description = data['description']

    # Automatically generate the movie code
    movie_code = generate_movie_code()

    try:
        async with async_session() as session:
            movie_id = await add_movie(
                session=session,
                movie_code=movie_code,
                movie_name=movie_name,
                movie_lang=movie_lang,
                thumb=thumb,
                movie_url=video_url,
                country=country,
                genre=genres,  # Store genres as a comma-separated string
                quality=quality,
                year=year,
                description=description,
                views=0
            )
        await bot.send_photo(
            chat_id=f'@{CHANNEL_LINK}',
            photo=thumb,
            caption=f"<b>🎬 Nom: {movie_name}\n\n</b>"
                    f"<b>➖➖➖➖➖➖➖\n\n</b>"
                    f"<b>🌍 Davlat: {country}\n</b>"
                    f"<b>🌐 Til: {movie_lang}\n</b>"
                    f"<b>⚡ Sifat: {quality}\n</b>"
                    f"<b>📅 Yil: {year}\n\n</b>"
                    f"<b>🔢 Film kodi:</b> <code>{movie_code}</code>\n"
                    f"<b><a href='https://t.me/{bot_info.username}?start=movie_{movie_code}'>TOMOSHA QILISH UCHUN BOSING</a></b>\n\n"
                    f"<b>🤖 Bot: @{bot_info.username}\n\n</b>"
                    f"<b>@{CHANNEL_LINK} | Filmlar olami 🍿</b>"
        )
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Kino muvaffaqiyatli qo'shildi:\n"
        )
    except Exception as e:
        logging.error(f"Kino qo'shishda xatolik: {e}")
        await message.answer("❌ Kino qo'shishda xatolik yuz berdi. Iltimos, keyinroq sinab ko'ring.")

    await message.answer("🔁 Yana bir kinoni qo'shish uchun 'start_add_movie' tugmasini bosing.",reply_markup=await admin_panels())

def generate_movie_code():
    """Generate a sequential movie code."""
    # Replace this with logic to fetch and increment the last used movie code from the database.
    movie_code = random.randint(1000, 9999)
    return str(movie_code)