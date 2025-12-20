from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    Database модель пользователя.

    :ivar id: ID пользователя.
    :ivar login: Логин.
    :ivar username: Username.
    :ivar password_hash: Хеш пароля.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    login: str = Field(index=True, unique=True)
    username: str
    password_hash: str


class Message(SQLModel, table=True):
    """
    Database модель сообщения.

    :ivar id: ID сообщения.
    :ivar sender_id: ID отправителя.
    :ivar receiver_id: ID получателя.
    :ivar content: Текст сообщения.
    :ivar is_readed: Бул прочитанности сообщения.
    :ivar timestamp: Время создания сообщения (UTC).
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    content: str
    is_readed: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
