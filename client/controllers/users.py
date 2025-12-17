from client.controllers.base import BaseController
from client.framework import command
from dto.models import UserListRequest
from client.logger import *

class UsersController(BaseController):

    @command("users")
    async def list_users(self, page: int = 1):
        """
        Вывод списка пользователей
        /users [Номер страницы]
        
        :param page: Страница
        :type page: int
        """
        log_info(f"Запрос списка пользователей (страница {page})...")
        request = UserListRequest(page=page)
        await self.ctx.send(request)

    @command("find")
    async def find_users(self, query: str):
        """
        Поиск пользователей
        /find [Username или Login]
        
        :param page: Username | Login
        :type page: str
        """
        log_info(f"Поиск пользователей по запросу '{query}'...")
        request = UserListRequest(search_query=query, page=1)
        await self.ctx.send(request)


