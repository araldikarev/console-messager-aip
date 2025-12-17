from client.controllers.base import BaseController
from client.framework import command
from client.logger import log_ok, log_error

class TokenController(BaseController):

    @command("token")
    async def print_token(self):
        """
        Выводит токен пользователя.
        /token
        """
        token = self.ctx.token
        if token is None:
            log_error("Токен не установлен - войдите или зарегистрируйтесь")
        else:
            log_ok(f"Ваш токен: {token}")