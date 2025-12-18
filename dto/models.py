from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class BasePacket(BaseModel):
    """
    Базовый пакет протокола - провайдит JWT токен.
    """

    token: Optional[str] = None
    """JWT токен пользователя (Опционально)."""


class RegisterRequest(BasePacket):
    """
    Пакет регистрации нового пользователя.
    """

    action: Literal["register"] = "register"
    """Тип пакета. Фиксированное значение 'register'."""

    login: str = Field(..., min_length=3, max_length=20)
    """Логин пользователя (длина 3–20 символов)."""

    username: str = Field(..., min_length=3, max_length=50)
    """Username пользователя (длина 3–50 символов)."""

    password_hash: str = Field(..., min_length=20)
    """Хеш пароля (минимальная длина 20 символов)."""


class LoginRequest(BasePacket):
    """
    Пакет авторизации существующего пользователя.
    """

    action: Literal["login"] = "login"
    """Тип пакета. Фиксированное значение 'login'."""

    login: str = Field(..., min_length=3, max_length=20)
    """Логин пользователя."""

    password_hash: str = Field(..., min_length=20)
    """Хеш пароля."""


class HistoryRequest(BasePacket):
    """
    Пакет запроса истории переписки с конкретным пользователем.
    """

    action: Literal["history"] = "history"
    """Тип пакета. Фиксированное значение 'history'."""

    target_user_id: int
    """ID собеседника."""

    limit: int = 20
    """Максимальное количество сообщений в ответе (опционально)."""


class SendMessageRequest(BasePacket):
    """
    Пакет отправки сообщения пользователю.
    """

    action: Literal["message"] = "message"
    """Тип пакета. Фиксированное значение 'message'."""

    receiver_id: int
    """ID получателя."""

    content: str
    """Текст сообщения."""


class IncomingMessagePacket(BaseModel):
    """
    Пакет входящего сообщения (сервер -> клиент).
    """

    sender_id: int
    """ID отправителя."""

    sender_login: str
    """Логин отправителя."""

    content: str
    """Текст сообщения."""

    timestamp: datetime
    """Время отправки сообщения."""


class ServerResponse(BasePacket):
    """
    Универсальный пакет ответа сервера.
    """

    action: Literal[
        "success",
        "error",
        "auth_success",
        "user_list_result",
        "new_message",
        "message_history_result",
    ]
    """Тип ответа (успех, ошибка, данные и т.д.)."""

    data: str | None
    """Данные ответа (JSON строка или сообщение)."""


class UserListRequest(BasePacket):
    """
    Пакет запроса списка пользователей.
    """

    action: Literal["user_list"] = "user_list"
    """Тип пакета. Фиксированное значение 'user_list'."""

    page: int = 1
    """Номер страницы (начиная с 1)."""

    page_size: int = 5
    """Размер страницы (количество пользователей в выдаче)."""

    search_query: Optional[str] = None
    """Строка поиска (логин или username)."""
