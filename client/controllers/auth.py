from client.controllers.base import BaseController
from client.framework import command
from dto.models import LoginRequest, RegisterRequest
import hashlib

class AuthController(BaseController):

    def _hash_password(self, password: str) -> str:
        """Метод для SHA256 хеширования пароля."""
        salted_pwd = password + "123451969"
        return hashlib.sha256(salted_pwd.encode('utf-8')).hexdigest()

    @command("login")
    async def login(self, login: str, password: str):

        request = LoginRequest(login=login, password_hash=self._hash_password(password))

        await self.ctx.send(request)

    @command("register")
    async def register(self, login: str, username: str, password: str):

        request = RegisterRequest(login=login, username=username, password_hash=self._hash_password(password))

        await self.ctx.send(request)
    
