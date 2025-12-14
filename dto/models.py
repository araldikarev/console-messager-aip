from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional

class BasePacket(BaseModel):
    token: Optional[str] = None

class RegisterRequest(BasePacket):
    action: Literal["register"] = "register"
    login: str = Field(..., min_length=3, max_length=20)
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str = Field(..., min_length=20)

class LoginRequest(BasePacket):
    action: Literal["login"] = "login"
    login: str = Field(..., min_length=3, max_length=20)
    password_hash: str = Field(..., min_length=20)

class SendMessageRequest(BasePacket):
    action: Literal["message"] = "message"
    receiver_id: int
    content: str

class IncomingMessagePacket(BaseModel):
    sender_id: int
    sender_login: str
    content: str
    timestamp: datetime

class ServerResponse(BasePacket):
    action: Literal["success", "error", "auth_success", "user_list_result", "new_message", "message_history_result"]
    data: str | None

class UserListRequest(BasePacket):
    action: Literal["user_list"] = "user_list"
    page: int = 1
    page_size: int = 5
    search_query: Optional[str] = None