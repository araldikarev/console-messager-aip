import json

from sqlmodel import select, or_, col

from server.framework import BaseController, action, authorized
from dto.models import UserListRequest
from server.db_models import User


class UsersController(BaseController):

    @action("user_list")
    @authorized
    async def get_users(self, req: UserListRequest):
        """
        Эндпоинт получения списка пользователей. Требует авторизации.

        :param self: self
        :param req: Пакет UserListRequest
        :type req: UserListRequest
        """
        async with self.ctx.create_session() as session:
            query = select(User)

            if req.search_query:
                search_filter = or_(
                    col(User.login).contains(req.search_query),
                    col(User.username).contains(req.search_query),
                )
                query = query.where(search_filter)

            offset = (req.page - 1) * req.page_size

            query = query.offset(offset).limit(req.page_size)

            result = await session.execute(query)
            users = result.scalars().all()

            users_data = [
                {"id": user.id, "login": user.login, "username": user.username}
                for user in users
            ]

            await self.ctx.reply("user_list_result", json.dumps(users_data))
