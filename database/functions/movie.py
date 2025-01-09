from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from database.models import Movie
import random
import string
import logging

# Helper function to generate movie ID (4 digits + 3 uppercase letters)
def generate_movie_id():
    digits = ''.join(random.choices(string.digits, k=4))  # 4 digits
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))  # 3 uppercase letters
    return digits + letters

# Adding a new movie to the database
async def add_movie(
        session: AsyncSession,
        movie_name: str,
        movie_lang: str,
        thumb: str,
        movie_code: str,
        movie_url: str,
        country: str,
        genre: str,
        quality: str,
        year: int,
        description: str,
        views: int = 0
) -> str:
    new_movie = Movie(
        movie_id=generate_movie_id(),  # Generates a unique movie_id
        movie_name=movie_name,
        movie_lang=movie_lang,
        thumb=thumb,
        movie_code=movie_code,
        movie_url=movie_url,
        country=country,
        genre=genre,
        quality=quality,
        year=year,
        description=description,
        views=views,
        movie_time=datetime.now()  # Use current timestamp for movie_time
    )

    session.add(new_movie)
    try:
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"Kino qo'shishda xatolik: {e}")
        raise e
    return new_movie.movie_id

# Selecting a movie by its movie_code
async def select_movie(movie_code: str, session: AsyncSession):
    stmt = select(Movie).filter_by(movie_code=movie_code)
    result = await session.execute(stmt)
    movie = result.scalars().first()
    return movie

async def top_10_most_viewed_movies(session: AsyncSession):
    stmt = select(Movie).order_by(Movie.views.desc()).limit(10)
    result = await session.execute(stmt)
    top_movies = result.scalars().all()
    return top_movies

async def random_movie(session: AsyncSession):
    stmt = select(Movie).order_by(func.random()).limit(1)  # PostgreSQL
    # For MySQL, use: stmt = select(Movie).order_by(func.rand()).limit(1)
    result = await session.execute(stmt)
    movie = result.scalars().first()
    return movie

# Getting all movies
async def all_movies(session: AsyncSession):
    result = await session.execute(select(Movie))
    return result.scalars().all()

# Incrementing the movie view count
async def increment_movie_count(session: AsyncSession, movie_id):
    movie = await select_movie(movie_id, session)
    if movie:
        movie.views += 1
        await session.commit()
        return True
    return False

# Counting the total number of movies
async def count_movies(session: AsyncSession):
    result = await session.execute(select(func.count(Movie.movie_id)))
    return result.scalar()

# Deleting a movie
async def delete_movie(session: AsyncSession, movie_id):
    movie = await select_movie(movie_id, session)
    if movie:
        await session.delete(movie)
        await session.commit()
        return True
    return False
