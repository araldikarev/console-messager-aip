from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    login: str = Field(index=True, unique=True)
    username: str
    password_hash: str