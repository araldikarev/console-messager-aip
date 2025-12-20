from client.controllers.base import BaseController
from client.framework import command
from client.logger import log_info
from dto.models import SendMessageRequest, HistoryRequest


class ChatController(BaseController):

    @command("msg")
    async def send_msg(self, user_id: int, content: str):
        """
        Отправка сообщения.
        /msg <ID пользователя> <текст сообщения>

        :param self: self
        :param user_id: ID получателя.
        :type user_id: int
        :param content: Текст для отправки.
        :type content: str
        """
        log_info(f"Отправка сообщения пользователю ID {user_id}...")
        request = SendMessageRequest(receiver_id=user_id, content=content)
        await self.ctx.send(request)

    @command("history")
    async def get_history(self, user_id: int):
        """
        История переписки.
        /history <ID пользователя>

        :param self: self
        :param user_id: ID собеседника.
        :type user_id: int
        """
        log_info(f"Запрос истории с пользователем ID {user_id}...")
        req = HistoryRequest(target_user_id=user_id)
        await self.ctx.send(req)
