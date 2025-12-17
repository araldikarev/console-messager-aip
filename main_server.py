import asyncio
import json
import base64
import argparse

from cryptography.fernet import Fernet

import security 
from server.framework import ServerRouter, ServerContext
from server.controllers.auth import AuthController
from server.controllers.users import UsersController
from server.controllers.chat import ChatController
from server.database import init_db, setup_database
from server.framework import CONNECTED_USERS

SERVER_PRIVATE_KEY = None
SERVER_PUBLIC_KEY = None

router = ServerRouter()
router.register(AuthController)
router.register(UsersController) 
router.register(ChatController) 

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, db_session_maker):
    """
    Функция для обработки сообщений клиентов.
    
    :param reader: Поток чтения.
    :type reader: asyncio.StreamReader
    :param writer: Поток записи.
    :type writer: asyncio.StreamWriter
    :param db_session_maker: Фабрика сессий с БД.
    """
    ctx = ServerContext(reader, writer, db_session_maker)
    address = writer.get_extra_info("peername")
    print(f"Подключение от {address}")

    try:
        print(f"[{address}] Начало HANDSHAKE")

        pem_key = security.public_key_to_pem(SERVER_PUBLIC_KEY)
        pem_base64 = base64.b64encode(pem_key)
        writer.write(pem_base64 + b"\n")
        await writer.drain()

        encrypted_fernet_key_base64 = await reader.readline()
        if not encrypted_fernet_key_base64:
            print("Клиент не поддержал Handshake")
            return
        
        fernet_key = security.decrypt_rsa(SERVER_PRIVATE_KEY, encrypted_fernet_key_base64.strip())
        ctx.cipher = Fernet(fernet_key)

        print(f"[{address}] Успешный HANDSHAKE! Канал зашифрован.")

        while True:
            encrypted_line = await reader.readline()
            if not encrypted_line:
                break
                
            encrypted_line = encrypted_line.strip()
            if not encrypted_line:
                continue

            try:
                json_bytes = ctx.cipher.decrypt(encrypted_line)
                message_str = json_bytes.decode('utf-8')
                print(f"Получено (дешифрованно): {message_str}")

                base_data = json.loads(message_str)
                await router.dispatch(ctx, base_data)
            except json.JSONDecodeError:
                print("Недействительный JSON")
                continue

    except Exception as ex:
        print(f"Произошла непредвиденная ошибка: {ex}")
    finally:
        if ctx.user_id and ctx.user_id in CONNECTED_USERS:
            del CONNECTED_USERS[ctx.user_id]
            print(f"[OFFLINE] Отключение пользователя {ctx.user_id}")
        print(f"Отключение: {address}")
        writer.close()
        await writer.wait_closed()

def parse_args():
    """
    Парсинг аргументов.
    """
    parser = argparse.ArgumentParser(description="Сервер консольного мессенджера")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="IP Хоста")
    parser.add_argument("--port", type=int, default=12000, help="Порт")
    parser.add_argument("--db-path", type=str, default="server/database.db", help="Путь к SQLite базе данных")
    parser.add_argument("--jwt-secret", default="UNSAFE_JWT_SECRET_KEY", help="JWT Секретный ключ")
    parser.add_argument("--jwt-algo", default="HS256", help="Алгоритм JWT")
    parser.add_argument("--jwt-exp", type=int, default=24, help="Часы истечения JWT")
    return parser.parse_args()

async def main():
    """
    Стартовая точка логики сервера.
    """
    global SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY
    args = parse_args()

    security.setup_jwt(args.jwt_secret, args.jwt_algo, args.jwt_exp)

    session_maker = setup_database(args.db_path)

    await init_db()

    print("Генерация RSA ключей сервера...")
    SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY = security.generate_rsa_keys()
    print("RSA ключи сгенерированы.")

    server_handler = lambda reader, writer: handle_client(reader, writer, session_maker)

    server = await asyncio.start_server(server_handler, args.host, args.port)
    async with server:
        print(f"Поднятие сервера на {args.host}:{args.port} (Путь к бд: {args.db_path})")
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
            