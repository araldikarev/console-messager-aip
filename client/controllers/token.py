from client.controllers.base import BaseController
from client.framework import command
from client.logger import *

class TokenController(BaseController):

    @command("token")
    async def print_token(self):
        token = self.ctx.token
        if token is None:
            log_error("Токен не установлен - войдите или зарегистрируйтесь")
        else:
            log_ok(f"Ваш токен: {token}")