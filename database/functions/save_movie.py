from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import SavedMovie
import random
import string
import logging

# Foydalanuvchi tomonidan saqlangan kino qo'shish funksiyasi
async def save_movie_to_db(
        session: AsyncSession,
        user_id: int,
        movie_code: str,
        movie_name: str,
        thumb: str,
        views: int = 0
) -> str:
    # Yangi saqlangan kino obyektini yaratish
    new_movie = SavedMovie(
        user_id=user_id,
        movie_name=movie_name,
        movie_code=movie_code,
        thumb=thumb,
        views=views,
    )

    session.add(new_movie)
    try:
        await session.commit()
        logging.info(f"Foydalanuvchi {user_id} {movie_name} filmini saqladi.")
        return new_movie.id  # return id of the saved movie
    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"Kino qo'shishda xatolik: {e}")
        raise e

async def select_saved_movie(movie_code: str, user_id: int, session: AsyncSession):
    stmt = select(SavedMovie).filter_by(movie_code=movie_code, user_id=user_id)
    result = await session.execute(stmt)
    return result.scalars().first()

# Foydalanuvchining saqlagan kinolarini olish
async def get_saved_movies(user_id: int, session: AsyncSession, page: int, page_size: int = 10):
    offset = (page - 1) * page_size
    result = await session.execute(
        select(SavedMovie).filter(SavedMovie.user_id == user_id).offset(offset).limit(page_size)
    )
    return result.scalars().all()

# Kino ko'rishlar sonini oshirish
async def increment_movie_views(session: AsyncSession, movie_code: str):
    movie = await select_saved_movie(movie_code, session)
    if movie:
        movie.views += 1
        await session.commit()
        return True
    return False

# Umumiy kinolar sonini hisoblash
async def count_saved_movies(session: AsyncSession):
    result = await session.execute(select(func.count(SavedMovie.id)))
    return result.scalar()

# Kino o'chirish
async def delete_saved_movie(session: AsyncSession, movie_code: str, user_id: int):
    movie = await select_saved_movie(movie_code=movie_code,user_id=user_id, session=session)
    if movie:
        await session.delete(movie)
        await session.commit()
        return True
    return False
