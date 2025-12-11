from dto.models import RegisterRequest
import asyncio
from aioconsole import ainput, aprint
from client.framework import CommandRouter, Context
from client.controllers.auth import AuthController
import base64
import security
from cryptography.fernet import Fernet

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
                print("Некорретные данные, разрыв соединения.")
                break

            data = data.strip()
            if not data: 
                continue

            if ctx.cipher:
                try:
                    decrypted = ctx.cipher.decrypt(data)
                    message_str = decrypted.decode('utf-8')
                    await aprint(f"\n[SERVER]: {message_str}")
                except Exception as e:
                    print(f"Ошибка дешифровки: {e}")
            
            else:
                print(f"Raw сообщение: {data}")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Ошибка чтения: {e}")

async def user_input_loop(writer: asyncio.StreamWriter, ctx: Context):
    await aprint("Ожидание handshake...")
    await handshake_completed.wait()

    router = CommandRouter(ctx)
    router.register_controller(AuthController)
    
    await aprint("Консольный мессенджер V1! Введите команду (например /login или /register)")

    while True:
        line = await ainput(">>> ")
        await router.dispatch(line)

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
        print(f"Ошибка HANDSHAKE: {e}")

async def main():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"Подключено к {HOST}:{PORT}")
    except ConnectionError as ex:
        print(f"Не удалось подключиться к серверу")
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

        print("Соединение закрыто")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass