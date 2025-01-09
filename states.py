from aiogram.fsm.state import State, StatesGroup

class AddMovieState(StatesGroup):
    waiting_for_video_url = State()
    waiting_for_name = State()
    waiting_for_lang = State()
    waiting_for_thumbnail = State()
    waiting_for_country = State()
    waiting_for_genre = State()
    waiting_for_quality = State()
    waiting_for_year = State()
    waiting_for_description = State()
    waiting_for_movie_code = State()

