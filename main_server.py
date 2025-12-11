import asyncio
import json
from server.framework import ServerRouter, ServerContext
from server.controllers.auth import AuthController
from server.database import init_db, async_session

router = ServerRouter()
router.register(AuthController)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    ctx = ServerContext(reader, writer, async_session)
    address = writer.get_extra_info("peername")
    print(f"Подключение от {address}")

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            
            message_str = data.decode('utf-8')
            print(f"Получено: {message_str}")

            try:
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
    await init_db()

    server = await asyncio.start_server(handle_client, "127.0.0.1", 12000)
    async with server:
        print("Поднятие сервера!")
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
            