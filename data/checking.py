from aiogram import Bot
from aiogram.types import ChatMember




async def check_subscription(user_id: int, channel_id: str) -> bool:
    try:
        # Get user status in the channel
        from app import bot
        chat_member = await bot.get_chat_member(channel_id, user_id)
        # Check if the user is a member of the channel
        if chat_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
            return True
        else:
            return False
    except Exception:
        return False  # If an error occurs (like the bot cannot check the user's membership), return False
