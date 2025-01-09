import logging
from aiogram.types import ChatJoinRequest, ChatMemberUpdated
from aiogram import F, Router

from database.database import async_session
from database.functions.channel_join import add_channel_join, select_channel_join, delete_channel_join

router = Router()

@router.chat_join_request()
async def join_request_handler(message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    print(message.chat)
    if message.chat.type == "private":
        logging.info('Joining request for user %s', user.first_name)
        # AsyncSession ni ishlatish
        async with async_session() as session:
            # Foydalanuvchini qo'shish
            check_user = await select_channel_join(session=session,user_id=user.id, channel_id=chat.id)
            if not check_user:
                await add_channel_join(session=session,user_id=user.id, channel_id=chat.id)


@router.chat_member()
async def chat_m_handler(message: ChatMemberUpdated):
    old = message.old_chat_member
    new = message.new_chat_member

    # AsyncSession ni ishlatish
    async with async_session() as session:
        # Agar foydalanuvchi kanalga qo'shilgan bo'lsa
        if new.status == 'member':
            # Kanalga qo'shilgan foydalanuvchining ma'lumotlarini saqlash
            pass  # Bu yerda qo'shish uchun kerakli kodni yozing (masalan, insert)

        # Agar foydalanuvchi kanalni tark etgan bo'lsa
        if new.status == "left":
            # Foydalanuvchini kanalga obuna bo'lishi haqida ma'lumotlarni o'chirish
            await delete_channel_join(session=session, user_id=message.from_user.id, channel_id=message.chat.id)
