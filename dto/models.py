from pydantic import BaseModel, Field
from typing import Literal

class BasePacket(BaseModel):
    pass

class RegisterRequest(BasePacket):
    action: Literal["register"] = "register"
    login: str = Field(..., min_length=3, max_length=20)
    username: str = Field(..., min_length=3, max_length=50)
    passwordHash: str = Field(..., min_length=20)

class LoginRequest(BasePacket):
    action: Literal["login"] = "login"
    login: str = Field(..., min_length=3, max_length=20)
    passwordHash: str = Field(..., min_length=20)

class SendMessageRequest(BasePacket):
    action: Literal["message"] = "message"
    to_user_id: int
    from_user_id: int
    content: str

class ServerResponse(BasePacket):
    action: Literal["success", "error"]
    data: str | None