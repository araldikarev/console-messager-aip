from server.framework import BaseController, action, authorized, CONNECTED_USERS
from server.db_models import Message, User
from dto.models import SendMessageRequest, IncomingMessagePacket


class ChatController(BaseController):

    @action(name="message")
    @authorized
    async def send_message(self, req: SendMessageRequest):
        sender_id = self.ctx.user_id
        
        async with self.ctx.create_session() as session:
            receiver = await session.get(User, req.receiver_id)
            if not receiver:
                await self.ctx.reply_error(f"Пользователь {req.receiver_id} не найден!")
            
            message = Message(
                sender_id=sender_id,
                receiver_id=req.receiver_id,
                content=req.content,
                is_readed=False
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
                    timestamp=message.timestamp
                )

                try:
                    await target_ctx.reply("new_message", packet.model_dump_json())
                except Exception as ex:
                    print("Произошла ошибка при отправке сообщения: {e}")

            await self.ctx.reply_success("Сообщение отправлено!")