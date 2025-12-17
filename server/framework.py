import asyncio
import inspect

from typing import Callable, Dict, Type
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession 
from functools import wraps

from dto.models import ServerResponse
from security import verify_jwt

CONNECTED_USERS: Dict[int, "ServerContext"] = {}

class ServerContext:
    """
    Класс контекста, подставляющийся в контроллеры.
    """
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, db_session_maker):
        self.reader = reader
        self.writer = writer
        self.db_session_maker = db_session_maker
        self.peer_name = writer.get_extra_info("peername")
        self.cipher = None
        self.user_id: int | None = None
    
    async def reply(self, status: str, data: str | None = None):
        """
        Функция для ответа клиенту.
        
        :param self: self
        :param status: Статус ответа (success, error и тд)
        :type status: str
        :param data: Данные для отправки
        :type data: str | None
        """
        response = ServerResponse(action=status, data=data)
        json_str = response.model_dump_json()

        if self.cipher:
            encrypted_payload = self.cipher.encrypt(json_str.encode('utf-8'))
            self.writer.write(encrypted_payload + b"\n")
        else: 
            payload = json_str + '\n'
            self.writer.write(payload.encode('utf-8'))
        await self.writer.drain()

    async def reply_error(self, error_messgage: str):
        await self.reply("error", error_messgage)
    
    async def reply_success(self, success_message: str):
        await self.reply("success", success_message)

    def create_session(self) -> AsyncSession:
        return self.db_session_maker()


def action(name: str):
    """
    Декоратор для эндпоинтов
    
    :param name: Название эндпоинта для роутинга
    :type name: str
    """
    def decorator(func):
        func._action_name = name
        return func
    return decorator

def authorized(func):
    """
    Декоратор проверки авторизации.
    
    :param func: Функция
    """
    @wraps(func)
    async def wrapper(self: BaseController, req: BaseModel):
        if not req.token:
            await self.ctx.reply_error("Unauthorized: Нет токена в запросе.")
            return
        
        payload = verify_jwt(req.token)
        if not payload:
            await self.ctx.reply_error("Unauthorized: Невалидный токен")
            return
        
        self.ctx.user_id = int(payload["sub"])
        await func(self, req)
    wrapper._action_name = getattr(func, "_action_name", None)
    return wrapper

class BaseController:
    """Класс-провайдер контекста."""
    def __init__(self, ctx: ServerContext):
        self.ctx = ctx

class ServerRouter:
    """
    Класс роутинга на эндпоинты
    """
    def __init__(self):
        self.routes: Dict[str, tuple[Type[BaseController], Callable]] = {}

    def register(self, controller_cls: Type[BaseController]):
        """
        Регистрирует контроллер с эндпоинтами.
        
        :param self: self
        :param controller_cls: Класс контроллера для регистрации.
        :type controller_cls: Type[BaseController]
        """
        for name, method in inspect.getmembers(controller_cls, predicate=inspect.isfunction):
            action_name = getattr(method, "_action_name", None)
            if action_name:
                self.routes[action_name] = (controller_cls, method)
                print(f"[ServerRouter] Регистрация действия: '{action_name}' -> {controller_cls.__name__}.{name}")

    
    async def dispatch(self, ctx: ServerContext, raw_json: dict):
        """
        Роутинг полученных данных на нужный эндпоинт.
        
        :param self: self
        :param ctx: Контекст
        :type ctx: ServerContext
        :param raw_json: Raw JSON строка
        :type raw_json: dict
        """
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