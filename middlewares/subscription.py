import asyncio
from aiogram import types, BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Union, Callable, Awaitable, Any, Dict

from database.database import async_session
from database.functions.channel import all_channels  # Fetch channels from DB
from data.checking import check_subscription  # Assuming this checks if the user is subscribed


class User_checkMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.channels_info = []  # List to store channel information
        asyncio.create_task(self.load_channels())  # Load channels asynchronously when bot starts

    async def load_channels(self):
        """
        Load channels from the database.
        """
        async with async_session() as session:
            self.channels_info = await all_channels(session)  # Fetch channels from the DB

    async def __call__(
        self,
        handler: Callable[[types.Update, Dict[str, Any]], Awaitable[Any]],  # Fix the type hint for the handler
        event: types.Update,  # Update event can be either message or callback_query
        data: Dict[str, Any]
    ) -> Any:
        """
        Middleware logic to check user subscriptions.
        """
        user_id = None  # Initialize user_id variable

        # Determine whether the event is a message or callback_query
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            return await handler(event, data)  # If not a message or callback query, proceed to handler

        k = []  # List of buttons for channels the user is not subscribed to
        force = False  # Flag to track if the user is missing subscriptions

        # Iterate through the channels from the database
        for channel in self.channels_info:
            channel_id = channel.channel_id
            try:
                from app import bot
                # Check if the user is a member of the channel
                res = await check_subscription(user_id, channel_id)  # This function should return a boolean
                kanals = await bot.get_chat(channel_id)  # Get channel details

                # If the user is not subscribed, add a button for that channel
                if not res:
                    k.append(InlineKeyboardButton(text=f"{kanals.title}", url=f"{channel.channel_link}"))
                    force = True
            except Exception as e:
                print(f"Error while checking subscription for channel {channel.channel_id}: {e}")
                continue  # In case of any error, skip to the next channel

        # If the user is not subscribed to one or more channels
        if force:
            builder = InlineKeyboardBuilder()
            builder.add(*k)  # Add the subscription buttons
            builder.add(InlineKeyboardButton(text="✅ Tekshirish", callback_data="check"))  # Add a check button
            builder.adjust(1)

            # Send a message with the inline keyboard to ask the user to subscribe to the missing channels
            await bot.send_message(
                chat_id=user_id,
                text="⚠️ Kechirasiz, botdan foydalanish uchun kanallarga obuna bo'lishingiz kerak.",
                reply_markup=builder.as_markup()
            )

            raise CancelHandler()  # Stop further processing of the event

        # If the user is subscribed to all channels, allow the handler to process the update
        return await handler(event, data)
