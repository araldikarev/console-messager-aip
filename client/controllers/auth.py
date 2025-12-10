from client.controllers.base import BaseController
from client.framework import command
from dto.models import LoginRequest, RegisterRequest

class AuthController(BaseController):

    @command("login")
    async def login(self, login: str, password: str):
        print(f"Введен Login на логинизацию: {login}")

        # Реализовать хеширование
        passwordHash = password + "HASHED"*10
        request = LoginRequest(login=login, passwordHash=passwordHash)

        await self.ctx.send(request)

    @command("register")
    async def register(self, login: str, username: str, password: str):
        print(f"Введен Login на регистрацию: {login}")

        # Реализовать хеширование
        passwordHash = password + "HASHED"*10
        request = RegisterRequest(login=login, username=username, passwordHash=passwordHash)

        await self.ctx.send(request)
    
