import asyncio
import json
from server.framework import ServerRouter, ServerContext
from server.controllers.auth import AuthController
from server.controllers.users import UsersController
from server.database import init_db, async_session
import security 
import base64
from cryptography.fernet import Fernet

SERVER_PRIVATE_KEY = None
SERVER_PUBLIC_KEY = None

router = ServerRouter()
router.register(AuthController)
router.register(UsersController) 

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    ctx = ServerContext(reader, writer, async_session)
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
            encrypted_line  = await reader.readline()
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
        print(f"Отключение: {address}")
        writer.close()
        await writer.wait_closed()

async def main():
    global SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY
    
    await init_db()

    print("Генерация RSA ключей сервера...")
    SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY = security.generate_rsa_keys()
    print("RSA ключи сгенерированы.")

    server = await asyncio.start_server(handle_client, "127.0.0.1", 12000)
    async with server:
        print("Поднятие сервера!")
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
            