from server.framework import BaseController, action
from dto.models import LoginRequest, RegisterRequest

class AuthController(BaseController):

    @action("login")
    async def login(self, req: LoginRequest):
        print(f"НА СЕРВЕР В LOGIN ЗАШЛИ СЛЕДУЮЩИЕ ДАННЫЕ: {req.model_dump_json()}")

        await self.ctx.reply_error("Не найден пользователь!")

    @action("register")
    async def register(self, req: RegisterRequest):
        print(f"НА СЕРВЕР В REGISTER ЗАШЛИ СЛЕДУЮЩИЕ ДАННЫЕ: {req.model_dump_json()}")

        await self.ctx.reply_error("Не найден пользователь!")