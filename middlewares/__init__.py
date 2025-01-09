from aiogram import Dispatcher

from .subscription import User_checkMiddleware
from .throttling import ThrottlingMiddleware

def setup(dp: Dispatcher):
    # dp.update.middleware(ThrottlingMiddleware())
    dp.message.middleware(User_checkMiddleware())
