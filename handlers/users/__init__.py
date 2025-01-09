from aiogram import Dispatcher

from .start import router as start_router
from .add_movie import router as add_router
from .get_movie import router as get_router
from .search_query import router as search_router
from .join_channel import router as join_router
from .like_page import router as like_page_router
from .top_films import router as top_films_router

def setup(dp: Dispatcher):
    dp.include_routers(
        start_router,
        add_router,
        get_router,
        search_router,
        join_router,
        like_page_router,
        top_films_router
    )