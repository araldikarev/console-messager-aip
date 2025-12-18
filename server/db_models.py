from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    Database модель пользователя.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    login: str = Field(index=True, unique=True)
    username: str
    password_hash: str


class Message(SQLModel, table=True):
    """
    Database модель сообщения.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    content: str
    is_readed: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
