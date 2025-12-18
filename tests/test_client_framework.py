import pytest
from unittest.mock import patch
from client.framework import CommandRouter, Context, command


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
    async def test_command(self, random_arg: str):
        """
        Тестовая команда

        :param self: self
        :param arg1: Случайный аргумент
        :type arg1: str
        """
        self.called = True
        self.last_argument = random_arg

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

    node = router.root.children["math"]
    controller_instance = node.handler.__self__

    await router.dispatch("/math abc")

    assert controller_instance.last_argument is None


async def test_dispatch_wrong_argument_count():
    """Негативный тест: неверное количество аргументов команды."""
    writer = MockWriter()
    ctx = Context(writer)
    router = CommandRouter(ctx)
    router.register_controller(MockController)

    node = router.root.children["math"]
    controller_instance = node.handler.__self__

    await router.dispatch("/math")

    assert controller_instance.last_argument is None
