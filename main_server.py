import asyncio
import json
from dto.models import LoginRequest, RegisterRequest, ServerResponse
from pydantic import ValidationError

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
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
            except json.JSONDecodeError:
                print("Недействительный JSON")
                continue

            match base_data.get("action"):
                case "login":
                    try:
                        request = LoginRequest.model_validate(base_data)
                        print(f"Попытка логина со следующими данными: {request}")

                        # Сделать проверку на существование логина
                        # Сделать проверку на соответствие хеша паролей

                        
                        response = ServerResponse(action="success", data="Успешный вход (ФЕЙК)")
                    except ValidationError as e:
                        response = ServerResponse(action="error", data=str(e))
                case "register":
                    try:
                        request = RegisterRequest.model_validate(base_data)
                        print(f"Попытка регистрации со следующими данными: {request}")
                        # Сделать проверку на существование логина

                        
                        response = ServerResponse(action="success", data="Успешная регистрация (ФЕЙК)")
                    except ValidationError as e:
                        response = ServerResponse(action="error", data=str(e))

            if response:
                response_str = response.model_dump_json() + '\n'
                writer.write(response_str.encode('utf-8'))
                await writer.drain()

    except Exception as ex:
        print(f"Произошла непредвиденная ошибка: {ex}")
    finally:
        print(f"Отключение: {address}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 12000)
    async with server:
        print("Поднятие сервера!")
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
            