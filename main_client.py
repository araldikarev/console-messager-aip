import asyncio
import base64
import json


from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from cryptography.fernet import Fernet


import security
from client.framework import CommandRouter, Context
from client.controllers.auth import AuthController
from client.controllers.users import UsersController
from client.controllers.token import TokenController
from client.controllers.chat import ChatController
from client.logger import *
from dto.models import IncomingMessagePacket


HOST = "127.0.0.1"
PORT = "12000"

handshake_completed = asyncio.Event()



async def listen_from_server(reader: asyncio.StreamReader, ctx: Context):
    """
    Фоновая задача: выводит сообщения на экран
    """
    try:
        while True:
            data = await reader.readline()
            if not data:
                log_error("Некорретные данные, разрыв соединения.")
                break

            data = data.strip()
            if not data: 
                continue

            if ctx.cipher:
                try:
                    decrypted = ctx.cipher.decrypt(data)
                    message_str = decrypted.decode('utf-8')
                except Exception as e:
                    log_error(f"Ошибка дешифровки: {e}")
            
            else:
                log_error(f"Raw сообщение: {data}")
                continue
            
            try:
                response_dict = json.loads(message_str)
                action = response_dict.get("action")
                content = response_dict.get("data")

                if action == "auth_success":
                    ctx.token = content
                    log_ok("\n[SYSTEM]: Успешная авторизация: Токен успешно установлен!\n")
                elif action == "user_list_result":
                    users = json.loads(content)
                    if not users:
                        log_info("\n[USERS]: Пользователи не найдены.\n")
                    else:
                        log_ok(f"\n{'ID':<5} | {'LOGIN':<15} | {'USERNAME':<20}")
                        log_ok("-" * 45)
                        for u in users:
                            log_info(f"{u['id']:<5} | {u['login']:<15} | {u['username']:<20}")
                        log_ok("-" * 45 + "\n")
                elif action == "new_message":
                    msg_dict = json.loads(content) 
                    msg = IncomingMessagePacket(**msg_dict)
                    
                    log_notify(f"\n>>> НОВОЕ СООБЩЕНИЕ ОТ {msg.sender_login} (ID {msg.sender_id}):")
                    log_info(f"    {msg.content}")
                    log_notify(">>>\n")
                elif action == "message_history_result":
                    history = json.loads(content)
                    if not history:
                        log_info("\n[HISTORY]: История пуста.\n")
                    else:
                        log_ok(f"\n{'- НАЧАЛО ИСТОРИИ -':^50}")
                        for item in history:
                            prefix = "Вы" if item['is_me'] else item['sender_login']
                            time_str = item['timestamp'].replace('T', ' ')[:16]
                            
                            if item['is_me']:
                                log_info(f"[{time_str}] {prefix}: {item['content']}")
                            else:
                                log_notify(f"[{time_str}] {prefix}: {item['content']}")
                        log_ok(f"{'- КОНЕЦ ИСТОРИИ -':^50}\n")
                elif action == "error":
                    log_error(f"\n[SYSTEM]: Ошибка: {content}\n")
                else:
                    log_info(f"\n[SERVER]: {message_str}\n")
            except json.JSONDecodeError:
                log_error("\n[SYSTEM]: Внутренняя ошибка парсинга JSON\n")
            except Exception as ex:
                log_error(f"\n[SYSTEM]: Произошла непредвиденная ошибка: {ex}")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        log_error(f"Ошибка чтения: {e}")

async def user_input_loop(writer: asyncio.StreamWriter, ctx: Context):
    log_info("Ожидание handshake...")
    await handshake_completed.wait()
    log_ok("Handshake успешно произведен!")

    router = CommandRouter(ctx)
    router.register_controller(AuthController)
    router.register_controller(UsersController)
    router.register_controller(ChatController)
    router.register_controller(TokenController)
    
    session = PromptSession()

    log_notify("Консольный мессенджер V1! Введите команду (например /login или /register)")

    while True:
        try: 
            line = await session.prompt_async(">>> ", style=style)
            await router.dispatch(line)
        except (EOFError, KeyboardInterrupt):
            return

async def perform_handshake(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, ctx: Context):
    """
    Обмен ключами
    """
    try:
        pem_base64 = await reader.readline()
        if not pem_base64:
            raise ConnectionError("Сервер закрыл соединение")
        
        pem_bytes = base64.b64decode(pem_base64)
        server_public_key = security.pem_to_public_key(pem_bytes)

        session_key = security.generate_fernet_key()

        encrypted_session_key = security.encrypt_rsa(server_public_key, session_key)

        writer.write(encrypted_session_key + b"\n")
        await writer.drain()

        ctx.cipher = Fernet(session_key)

        handshake_completed.set()
    except Exception as e:
        log_error(f"Ошибка HANDSHAKE: {e}")

async def main():
    with patch_stdout():
        try:
            reader, writer = await asyncio.open_connection(HOST, PORT)
            log_ok(f"Подключено к {HOST}:{PORT}")
        except ConnectionError as ex:
            log_error(f"Не удалось подключиться к серверу: {ex}", style=style)
            return
        
        ctx = Context(writer)

        try:
            await perform_handshake(reader, writer, ctx)
        except Exception:
            writer.close()
            return

        listener_task = asyncio.create_task(listen_from_server(reader, ctx))

        
        try: 
            await user_input_loop(writer, ctx)
        finally:
            listener_task.cancel()
            writer.close()
            await writer.wait_closed()

            log_info("Соединение закрыто")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass