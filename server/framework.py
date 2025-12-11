import asyncio
import inspect
from typing import Callable, Dict, Type
from pydantic import BaseModel, ValidationError
from dto.models import ServerResponse
from sqlalchemy.ext.asyncio import AsyncSession 

class ServerContext:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, db_session_maker):
        self.reader = reader
        self.writer = writer
        self.db_session_maker = db_session_maker
        self.peer_name = writer.get_extra_info("peername")
    
    async def reply(self, status: str, data: str | None = None):
        """Ответ клиенту"""
        response = ServerResponse(action=status, data=data)

        payload = response.model_dump_json() + '\n'
        self.writer.write(payload.encode('utf-8'))
        await self.writer.drain()

    async def reply_error(self, error_messgage: str):
        await self.reply("error", error_messgage)
    
    async def reply_success(self, success_message: str):
        await self.reply("success", success_message)

    def create_session(self) -> AsyncSession:
        return self.db_session_maker()

def action(name: str):
    def decorator(func):
        func._action_name = name
        return func
    return decorator

class BaseController:
    def __init__(self, ctx: ServerContext):
        self.ctx = ctx

class ServerRouter:
    def __init__(self):
        self.routes: Dict[str, tuple[Type[BaseController], Callable]] = {}

    def register(self, controller_cls: Type[BaseController]):

        for name, method in inspect.getmembers(controller_cls, predicate=inspect.isfunction):
            action_name = getattr(method, "_action_name", None)
            if action_name:
                self.routes[action_name] = (controller_cls, method)
                print(f"[ServerRouter] Регистрация действия: '{action_name}' -> {controller_cls.__name__}.{name}")

    
    async def dispatch(self, ctx: ServerContext, raw_json: dict):
        """Поиск эндпоинта и парсинг аргументов"""
        action_name = raw_json.get("action")

        if not action_name:
            await ctx.reply_error("Не найден эндпоинт")
            return
        
        handler_info = self.routes.get(action_name)
        if not handler_info:
            await ctx.reply_error(f"Неизвестный action: {action_name}")
            return
        
        controller_cls, method = handler_info

        controller_instance = controller_cls(ctx)

        signature = inspect.signature(method)
        params = list(signature.parameters.values())

        request = None

        if len(params) > 1:
            param_type = params[1].annotation
            if issubclass(param_type, BaseModel):
                try:
                    request = param_type.model_validate(raw_json)
                except ValidationError as e:
                    print(f"Ошибка валидации JSON: {e}")
                    await ctx.reply_error(f"Ошибка валидации JSON: {e}")
                    return
            
            else:
                request = raw_json
        
        try:
            if request:
                await method(controller_instance, request)
            else:
                await method(controller_instance)
        except Exception as e:
            print(f"Внутренняя ошибка в хендлере: {e}")
            await ctx.reply_error("Внутренняя ошибка сервера")