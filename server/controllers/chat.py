import json

from sqlmodel import select, or_, and_, col

from server.framework import BaseController, action, authorized, CONNECTED_USERS
from server.db_models import Message, User
from dto.models import SendMessageRequest, IncomingMessagePacket, HistoryRequest


class ChatController(BaseController):

    @action(name="message")
    @authorized
    async def send_message(self, req: SendMessageRequest):
        """
        Эндпоинт отправки сообщения пользователю. Требует авторизации.

        :param self: self
        :param req: Пакет SendMessageRequest
        :type req: SendMessageRequest
        """
        sender_id = self.ctx.user_id

        async with self.ctx.create_session() as session:
            receiver = await session.get(User, req.receiver_id)
            if not receiver:
                await self.ctx.reply_error(f"Пользователь {req.receiver_id} не найден!")
                return

            message = Message(
                sender_id=sender_id,
                receiver_id=req.receiver_id,
                content=req.content,
                is_readed=False,
            )
            session.add(message)
            await session.commit()

            sender = await session.get(User, sender_id)

            if req.receiver_id in CONNECTED_USERS:
                target_ctx = CONNECTED_USERS[req.receiver_id]

                packet = IncomingMessagePacket(
                    sender_id=sender_id,
                    sender_login=sender.login,
                    content=req.content,
                    timestamp=message.timestamp,
                )

                try:
                    await target_ctx.reply("new_message", packet.model_dump_json())
                    message.is_readed = True
                    await session.commit()
                except Exception as ex:
                    print(f"Произошла ошибка при отправке сообщения: {ex}")

            await self.ctx.reply_success("Сообщение отправлено!")

    @action("history")
    @authorized
    async def get_history(self, req: HistoryRequest):
        """
        Эндпоинт получения истории сообщений с пользователем. Требует авторизации.

        :param self: self
        :param req: Пакет HistoryRequest
        :type req: HistoryRequest
        """
        my_id = self.ctx.user_id
        target_id = req.target_user_id
        async with self.ctx.create_session() as session:
            query = (
                select(Message, User.login)
                .join(User, User.id == Message.sender_id)
                .where(
                    or_(
                        and_(
                            Message.sender_id == my_id, Message.receiver_id == target_id
                        ),
                        and_(
                            Message.sender_id == target_id, Message.receiver_id == my_id
                        ),
                    )
                )
                .order_by(col(Message.timestamp).desc())
                .limit(req.limit)
            )

            result = await session.execute(query)

            rows = result.all()

            rows = rows[::-1]

            history_data = []
            for message, sender_login in rows:
                history_data.append(
                    {
                        "sender_login": sender_login,
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat(),
                        "is_me": message.sender_id == my_id,
                    }
                )
            await self.ctx.reply("message_history_result", json.dumps(history_data))
