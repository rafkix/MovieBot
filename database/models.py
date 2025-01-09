from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# User jadvali
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    lang = Column(String, default="uz")
    user_time = Column(DateTime, default=datetime.utcnow)
    referral = Column(Integer, ForeignKey("users.user_id"), nullable=True)

class Movie(Base):
    __tablename__ = 'movies'

    movie_id = Column(String, primary_key=True, index=True)  # Unikal film ID si
    movie_lang = Column(String) # Film tili (masalan, O'zbek, Ingliz, Rus)
    thumb = Column(String) # Filmning rasmli miniatura tasviri (URL formatida)
    movie_url = Column(String) # Filmga havola (URL orqali ko'rish mumkin)
    movie_name = Column(String) # Film nomi
    country = Column(String) # Filmning chiqarilgan davlati (masalan, AQSH, Buyuk Britaniya)
    genre = Column(String) # Filmning janri (masalan, Sarguzasht, Drama, Komediya)
    quality = Column(String) # Filmning sifat (masalan, 1080p, 4K, HD)
    year = Column(Integer) # Filmning chiqarilgan yili
    views = Column(Integer, default=0) # Filmni ko'rganlar soni
    description = Column(String) # Filmning tavsifi (detallangan tushuntirish)
    movie_code = Column(String, unique=True,index=True)  # Film kodi (filmingizni noyob tarzda identifikatsiya qilish uchun)
    movie_time = Column(DateTime, nullable=True,
                        default=func.now)  # Film qo'shilgan vaqti (tizimda qo'shilgan sanasi va vaqti)

# class Series(Base):
#     __tablename__ = 'movies'
#
#     series_id = Column(String, primary_key=True, index=True)  # Unikal film ID si
#     series_name = Column(String)  # Film nomi
#     series_url = Column(String)  # Filmga havola
#     season = Column(Integer, nullable=True)  # Mavsum raqami
#     episode = Column(Integer, nullable=True)  # Epizod raqami
#     series_code = Column(String, unique=True, index=True)  # Seriya kodi
#     quality = Column(String)  # Filmning sifat
#     year = Column(Integer)  # Filmning chiqarilgan yili
#     views = Column(Integer, default=0)  # Filmni ko'rganlar soni
#     series_time = Column(DateTime, nullable=True, default=func.now)  # Film qo'shilgan vaqti


class SavedMovie(Base):
    __tablename__ = 'saved_movies'

    id = Column(Integer, primary_key=True)  # Auto-incremented ID for saved movie entry
    user_id = Column(Integer, nullable=False)  # ID of the user who saved the movie
    movie_code = Column(String, nullable=False)  # The unique movie code
    movie_name = Column(String, nullable=False)  # The name of the movie
    thumb = Column(String)
    views = Column(Integer, default=0)  # Number of views for the movie (optional)

class Channel(Base):
    __tablename__ = 'channels'

    channel_id = Column(Integer, primary_key=True, autoincrement=True)  # Kanalning unikal ID si
    channel_link = Column(String, nullable=False)  # Kanalning havolasi
    channel_time = Column(DateTime, default=datetime.utcnow)  # Kanalga qo'shilgan vaqt
    is_private = Column(String)

class ChannelJoin(Base):
    __tablename__ = 'channel_join'  # Tablitsa nomidagi xatolik tuzatildi

    id = Column(Integer, primary_key=True, autoincrement=True)  # Yozuvning unikal identifikatori
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Foydalanuvchi ID si
    channel_id = Column(Integer, ForeignKey("channels.channel_id"), nullable=False)  # Kanal ID si
    channel_time = Column(DateTime, default=datetime.utcnow)  # Qo'shilgan vaqt
