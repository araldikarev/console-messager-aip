from client.controllers.base import BaseController
from client.framework import command
from dto.models import LoginRequest, RegisterRequest
import hashlib

class AuthController(BaseController):

    def _hash_password(self, password: str) -> str:
        """
        Метод для SHA256 хеширования пароля.
        
        :param self: self
        :param password: Пароль.
        :type password: str
        :return: Захешированный пароль.
        :rtype: str
        """
        salted_pwd = password*5
        return hashlib.sha256(salted_pwd.encode('utf-8')).hexdigest()

    @command("login")
    async def login(self, login: str, password: str):
        """
        Команда авторизации.
        /login <login> <password>
        
        :param self: self
        :param login: Логин пользователя.
        :type login: str
        :param password: Пароль пользователя.
        :type password: str
        """
        request = LoginRequest(login=login, password_hash=self._hash_password(password))

        await self.ctx.send(request)

    @command("register")
    async def register(self, login: str, username: str, password: str):
        """
        Команда регистрации.
        /login <login> <username> <password>
        
        :param self: self
        :param login: Логин пользователя.
        :type login: str
        :param username: Username пользователя.
        :type username: str
        :param password: Пароль пользователя.
        :type password: str
        """
        request = RegisterRequest(login=login, username=username, password_hash=self._hash_password(password))

        await self.ctx.send(request)
    
