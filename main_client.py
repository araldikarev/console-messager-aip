from dto.models import RegisterRequest
import asyncio
import json
from aioconsole import ainput, aprint
from client.framework import CommandRouter, Context
from client.controllers.auth import AuthController

HOST = "127.0.0.1"
PORT = "12000"

async def listen_from_server(reader: asyncio.StreamReader):
    """
    Фоновая задача: выводит сообщения на экран
    """
    try:
        while True:
            data = await reader.readline()
            if not data:
                print("Некорретные данные, разрыв соединения.")
                break
            
            message_str = data.decode('utf-8').strip()
            
            await aprint(f"\n[SERVER]: {message_str}")
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Ошибка чтения: {e}")

async def user_input_loop(writer: asyncio.StreamWriter):
    ctx = Context(writer=writer)
    router = CommandRouter(ctx)

    router.register_controller(AuthController)
    
    await aprint("Консольный мессенджер V1")

    while True:
        line = await ainput(">>> ")
        await router.dispatch(line)



async def main():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"Подключено к {HOST}:{PORT}")
    except ConnectionError as ex:
        print(f"Не удалось подключиться к серверу")
        return

    listener_task = asyncio.create_task(listen_from_server(reader))

    try: 
        await user_input_loop(writer)
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