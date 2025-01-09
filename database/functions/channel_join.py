from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, delete
from database.models import ChannelJoin  # O'zgartiring, to'g'ri modelni import qiling

# Kanal qo‘shish
async def add_channel_join(session: AsyncSession, user_id: int, channel_id: int):
    # Kanal bazada bor yoki yo'qligini tekshirish
    result = await session.execute(
        select(ChannelJoin).where(ChannelJoin.channel_id == channel_id)
    )
    existing_channel = result.scalars().first()

    if existing_channel:
        return False  # Kanal allaqachon mavjud

    # Yangi kanal qo‘shish
    new_channel = ChannelJoin(user_id=user_id,channel_id=channel_id)
    session.add(new_channel)
    await session.commit()
    return True

# Kanal ma'lumotini olish
async def select_channel_join(user_id: int, session: AsyncSession):
    stmt = select(ChannelJoin).filter_by(user_id=user_id)

    # Execute the statement
    result = await session.execute(stmt)

    # Get the first matching result (if any)
    channel = result.scalars().first()

    return channel

async def get_all_pending_requests(session, channel_id: int):
    """
    Kanal uchun barcha qo'shilish so'rovlarini olish.
    """
    result = await session.execute(
        select(ChannelJoin).where(ChannelJoin.channel_id == channel_id)
    )
    return result.scalars().all()


# Barcha kanallarni olish
async def all_channels(session: AsyncSession):
    result = await session.execute(select(ChannelJoin))
    return result.scalars().all()

# Kanal ma'lumotini yangilash
async def update_channel(session: AsyncSession, channel_id: int, new_link: str):
    channel = await select_channel_join(channel_id, session)  # Fix argument order here
    if channel:
        channel.channel_link = new_link
        await session.commit()
        return True
    return False

# Kanallar sonini hisoblash
async def count_channels_join(session: AsyncSession):
    result = await session.execute(select(func.count(ChannelJoin.channel_id)))
    return result.scalar()

async def delete_channel_join(session: AsyncSession, user_id: int):
    # Kanal va foydalanuvchi bog'lanishini topish
    result = await session.execute(
        select(ChannelJoin).where(
            ChannelJoin.user_id == user_id
        )
    )
    channel = result.scalars().first()

    # Agar topilsa, o'chirish
    if channel:
        await session.delete(channel)
        await session.commit()
        return True

    # Agar topilmasa
    return False

async def delete_all_requests(session, channel_id: int):
    """
    Kanalga tegishli barcha so'rovlarni o'chirish.
    """
    await session.execute(
        delete(ChannelJoin).where(ChannelJoin.channel_id == channel_id)
    )
    await session.commit()
