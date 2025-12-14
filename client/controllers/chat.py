from client.controllers.base import BaseController
from client.framework import command
from dto.models import SendMessageRequest
from client.logger import *

class ChatController(BaseController):

    @command("msg")
    async def send_msg(self, user_id: int, content: str):
        """
        Отправка сообщения.
        /msg <ID пользователя> <Текст сообщения>
        """
        log_info(f"Отправка сообщения пользователю ID {user_id}...")
        request = SendMessageRequest(
            receiver_id=user_id,
            content=content
        )
        await self.ctx.send(request)