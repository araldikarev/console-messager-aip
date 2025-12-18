import inspect
import asyncio
from typing import Callable, Dict

from pydantic import BaseModel

from client.logger import log_info, log_error


class Context:
    """Контекст: передаётся в контроллеры."""

    def __init__(self, writer: asyncio.StreamWriter):
        self._writer = writer
        self.cipher = None
        self.token: str | None = None

    async def send(self, packet: BaseModel):
        """
        Отправляет данные на сервер.

        :param self: self
        :param packet: Отправляемый пакет данных.
        :type packet: BaseModel
        """
        if self.token and hasattr(packet, "token") and packet.token is None:
            packet.token = self.token

        data_str = packet.model_dump_json()

        if self.cipher:
            raw_bytes = data_str.encode("utf-8")
            encrypted_payload = self.cipher.encrypt(raw_bytes)
            self._writer.write(encrypted_payload + b"\n")
        else:
            payload = (data_str + "\n").encode("utf-8")
            self._writer.write(payload)

        await self._writer.drain()


def command(name: str):
    """
    Декоратор команды для регистрации.

    :param name: Название команды.
    :type name: str
    """

    def decorator(target):
        target._cmd_name = name
        target._is_command_node = True
        return target

    return decorator


class CommandNode:
    """Класс ноды команды. Необходим для роутинга (Пример: /command subcommand **arguments)"""

    def __init__(self, name: str, handler: Callable = None):
        """
        Инициализирует командную ноду.

        :param self: self
        :param name: Название ноды.
        :type name: str
        :param handler: Хендлер (исполняемая функция, опционально).
        :type handler: Callable
        """
        self.name = name
        self.children: Dict[str, "CommandNode"] = {}
        self.handler = handler
        self.is_group = handler is None

    def add_child(self, node: "CommandNode"):
        """
        Добавляет в ноду ветки (другую ноду)

        :param self: self
        :param node: Командная нода.
        :type node: "CommandNode"
        """
        self.children[node.name] = node


class CommandRouter:
    """Роутер зарегистрированных консольных команд."""

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.root = CommandNode("root")

    def register_controller(self, controller_cls):
        """
        Регистрация контроллера с командами.

        :param self: self
        :param controller_cls: Класс контроллера.
        """
        self._scan_recursive(controller_cls, self.root)

    def _scan_recursive(self, cls_def, parent_node: CommandNode):
        """
        Рекурсивное сканирование класса в поисках команд (хендлеров).

        :param self: self.
        :param cls_def: Класс контроллера.
        :param parent_node: Родительская нода.
        :type parent_node: CommandNode
        """
        instance = cls_def(self.ctx)

        current_node = parent_node
        cls_name = getattr(cls_def, "_cmd_name", None)

        if cls_name:
            if cls_name not in parent_node.children:
                group_node = CommandNode(cls_name)
                self.root.add_child(group_node)
            parent_node = parent_node.children[cls_name]
            log_info(f"[ROUTER] Группа: {cls_name}")

        for name, member in inspect.getmembers(instance, predicate=inspect.ismethod):
            if getattr(member, "_is_command_node", False):
                cmd_name = getattr(member, "_cmd_name")
                leaf_node = CommandNode(cmd_name, handler=member)
                current_node.add_child(leaf_node)
                log_info(f"... -> Метод: {cmd_name}")

        for name, member in inspect.getmembers(instance, predicate=inspect.isclass):
            if getattr(member, "_is_command_node", False):
                self._scan_recursive(member, current_node)

    async def dispatch(self, line: str):
        """
        Парсит строку и роутит по нужным командам.

        :param self: self
        :param line: Текстовая строка для парсинга.
        :type line: str
        """
        parts = line.strip().split()
        if not parts:
            return

        if parts[0].startswith("/"):
            parts[0] = parts[0][1:]

        node = self.root
        idx = 0
        while idx < len(parts):
            token = parts[idx].lower()
            if token in node.children:
                node = node.children[token]
                idx += 1
            else:
                break

        if node.is_group:
            options = list(node.children.keys())
            log_info(f"Выберите нужную команду: {options}")
            return

        handler = node.handler

        if handler is None:
            log_error("Неизвестная команда")
            return

        raw_args = parts[idx:]
        signature = inspect.signature(handler)
        params = list(signature.parameters.values())

        if len(raw_args) > len(params):
            last_param_idx = len(params) - 1
            if params[last_param_idx].annotation == str:
                tail = " ".join(raw_args[last_param_idx:])
                raw_args = raw_args[:last_param_idx]
                raw_args.append(tail)

        if len(raw_args) != len(params):
            hint = " ".join([f"<{p.name}:{p.annotation.__name__}>" for p in params])
            log_error(f"Ошибка аргументов. Формат: ... {node.name} {hint}")
            return

        try:
            converted_args = []
            for i, param in enumerate(params):
                value = raw_args[i]
                target_type = param.annotation
                if target_type is not inspect.Parameter.empty:
                    converted_args.append(target_type(value))
                else:
                    converted_args.append(value)

            await handler(*converted_args)
        except ValueError as e:
            log_error(f"Неверный тип данных: {e}")
        except Exception as e:
            log_error(f"Ошибка выполнения: {e}")
