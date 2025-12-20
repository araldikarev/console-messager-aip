import pytest
from unittest.mock import patch

from client.framework import CommandRouter, Context, command
from client.exceptions import (
    ValueErrorCommandException,
    ArgumentMismatchCommandException,
)


class MockWriter:
    """Mock для asyncio.StreamWriter"""

    def write(self, data):
        pass

    async def drain(self):
        pass


class MockController:
    """Mock для контроллера консольных команд"""

    def __init__(self, ctx):
        self.ctx = ctx
        self.called = False
        self.last_argument = None

    @command("test")
    async def test_command(self, last_arg: str):
        """
        Тестовая команда

        :param self: self
        :param last_arg: Последний аргумент
        :type last_arg: str
        """
        self.called = True
        self.last_argument = last_arg

    @command("math")
    async def math_command(self, num: int):
        """
        Добавляет десятку к числу

        :param self: self
        :param num: Число
        :type num: int
        """
        self.last_argument = num + 10


@pytest.fixture(autouse=True)
def mock_logger():
    """Отключение print логгера."""
    with patch("client.logger.print_formatted_text"):
        yield


async def test_router_registration():
    """Тест: контроллер регистрируется и строит ноды команд"""
    mock_writer = MockWriter()
    ctx = Context(mock_writer)
    router = CommandRouter(ctx)

    router.register_controller(MockController)

    assert "test" in router.root.children
    assert "math" in router.root.children


async def test_router_registration_bad_controller_raises():
    """Негативный тест: контроллер, не принимающий контекст, вызывает TypeError"""

    class BadController:
        def __init__(self):
            pass

    mock_writer = MockWriter()
    ctx = Context(mock_writer)
    router = CommandRouter(ctx)

    with pytest.raises(TypeError):
        router.register_controller(BadController)


async def test_dispatch_simple_command():
    """Тест: вызов команды /test hello"""
    mock_writer = MockWriter()
    ctx = Context(mock_writer)
    router = CommandRouter(ctx)

    router.register_controller(MockController)

    node = router.root.children["test"]
    controller_instance = node.handler.__self__

    await router.dispatch("/test hello")

    assert controller_instance.called is True
    assert controller_instance.last_argument == "hello"


async def test_dispatch_type_conversion():
    """Тест: аргумент int должен сконвертироваться из строки"""
    mock_writer = MockWriter()
    ctx = Context(mock_writer)
    router = CommandRouter(ctx)
    router.register_controller(MockController)

    node = router.root.children["math"]
    controller_instance = node.handler.__self__

    await router.dispatch("/math 5")

    # 5 + 10 = 15
    assert controller_instance.last_argument == 15


async def test_dispatch_unknown_command():
    """Негативный тест: несуществующая команда"""
    mock_writer = MockWriter()
    ctx = Context(mock_writer)
    router = CommandRouter(ctx)

    try:
        await router.dispatch("/unknown arg")
    except Exception as e:
        pytest.fail(f"Dispatch упал на неизвестной команде: {e}")


async def test_dispatch_wrong_argument_type():
    """Негативный тест: неверный тип аргумента."""
    writer = MockWriter()
    ctx = Context(writer)
    router = CommandRouter(ctx)
    router.register_controller(MockController)

    with pytest.raises(ValueErrorCommandException):
        await router.dispatch("/math abc")


async def test_dispatch_wrong_argument_count():
    """Негативный тест: неверное количество аргументов команды."""
    writer = MockWriter()
    ctx = Context(writer)
    router = CommandRouter(ctx)
    router.register_controller(MockController)

    with pytest.raises(ArgumentMismatchCommandException):
        await router.dispatch("/math")
