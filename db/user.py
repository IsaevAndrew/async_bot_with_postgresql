from .base import Base
from sqlalchemy.orm import sessionmaker, selectinload

from sqlalchemy import Column, Integer, String, Boolean, Date, select
import datetime


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, unique=True, primary_key=True)  # ТГ id
    username = Column(String(64), nullable=True)  # ТГ ник
    start_date = Column(Date, default=datetime.date.today)  # Дата
    fio = Column(String(255), nullable=True, default='')  # ФИО пользователя
    company = Column(String(255), nullable=True,
                     default='')  # Название компании
    phone = Column(String(20), nullable=True, default='')  # Номер телефона
    email = Column(String(255), nullable=True, default='')  # Электронная почта
    city = Column(String(100), nullable=True, default='')  # Город
    is_registered = Column(Boolean, default=False)  # Зарегистрован
    agrees_to_video = Column(Boolean, default=False)  # Отсылать видео


async def get_or_create_user(user_id: int, username: str,
                             session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=username
                )
                session.add(user)
                await session.commit()
            else:
                return user


async def update_user_info(user_id: int, fio: str, company: str, phone: str,
                           email: str, city: str,
                           session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                user.fio = fio
                user.company = company
                user.phone = phone
                user.email = email
                user.city = city
                user.is_registered = True
                await session.commit()


async def check_registration_status(user_id: int,
                                    session_maker: sessionmaker) -> bool:
    async with session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user.is_registered


async def check_agrees_to_video(user_id: int,
                                session_maker: sessionmaker) -> bool:
    async with session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user.agrees_to_video


async def update_agrees_to_video(user_id: int,
                                 session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                user.agrees_to_video = True
                await session.commit()


async def get_users_agreeing_to_video(session_maker: sessionmaker) -> list:
    async with session_maker() as session:
        async with session.begin():
            stmt = select(User.user_id).where(User.agrees_to_video == True)
            result = await session.execute(stmt)
            user_ids = [user_id for (user_id,) in result.fetchall()]
            return user_ids
