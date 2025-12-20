import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

import security
from server.controllers.auth import AuthController
from server.controllers.chat import ChatController
from server.db_models import User, Message
from server.exceptions import UnauthorizedError
from dto.models import RegisterRequest, SendMessageRequest


class MockServerContext:
    """Mock серверного контекста."""

    def __init__(self, session_maker):
        self.db_session_maker = session_maker
        self.replies = []
        self.user_id = None
        self.connected_users = {}

    def create_session(self):
        return self.db_session_maker()

    async def reply(self, status, data=None):
        self.replies.append((status, data))

    async def reply_error(self, message):
        self.replies.append(("error", message))

    async def reply_success(self, message):
        self.replies.append(("success", message))


@pytest.fixture
async def db_session_maker():
    """Создаёт БД сессию."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield maker

    await engine.dispose()


async def test_sing_up_saves_to_db(db_session_maker):
    """Тест: регистрации пользователя."""
    ctx = MockServerContext(db_session_maker)
    controller = AuthController(ctx)

    req = RegisterRequest(
        login="test_user", username="Test User", password_hash="hash123" * 5
    )

    await controller.register(req)

    assert ctx.replies[0][0] == "auth_success"

    async with db_session_maker() as session:
        result = await session.execute(select(User).where(User.login == "test_user"))
        user = result.scalars().first()
        assert user is not None
        assert user.username == "Test User"


async def test_chat_saves_history(db_session_maker):
    """Тест: создаётся 2 пользователя в БД, инициализируется ChatController, производится отправка сообщения от пользователя User 1 до пользователя User 2."""
    async with db_session_maker() as session:
        user1 = User(login="user1", username="User 1", password_hash="123")
        user2 = User(login="user2", username="User 2", password_hash="123")
        session.add(user1)
        session.add(user2)
        await session.commit()
        user1_id = user1.id
        user2_id = user2.id

    ctx = MockServerContext(db_session_maker)
    ctx.user_id = user1_id

    controller = ChatController(ctx)

    token = security.create_jwt(user1_id, "User 1")

    message_req = SendMessageRequest(
        token=token, receiver_id=user2_id, content="Hello from DB"
    )

    await controller.send_message(message_req)

    assert ctx.replies[0][0] == "success"

    async with db_session_maker() as session:
        result = await session.execute(select(Message))
        messages = result.scalars().all()
        assert len(messages) == 1
        message = messages[0]
        assert message.content == "Hello from DB"
        assert message.sender_id == user1_id
        assert message.receiver_id == user2_id


async def test_register_duplicate_login(db_session_maker):
    """Негативный тест: попытка регистрации с занятым логином"""
    security.setup_jwt("secret", "HS256", 1)
    ctx = MockServerContext(db_session_maker)
    controller = AuthController(ctx)

    req = RegisterRequest(
        login="duplicate_login", username="First User", password_hash="hash" * 5
    )

    await controller.register(req)
    assert ctx.replies[0][0] == "auth_success"

    await controller.register(req)

    assert ctx.replies[1][0] == "error"
    assert "занят" in ctx.replies[1][1]


async def test_chat_unauthorized_token(db_session_maker):
    """Негативный тест: отправка сообщения с невалидным токеном токеном"""
    security.setup_jwt("secret", "HS256", 1)
    ctx = MockServerContext(db_session_maker)
    controller = ChatController(ctx)

    bad_token = "some.bad.token"

    msg_req = SendMessageRequest(receiver_id=1, content="Сообщение.", token=bad_token)

    with pytest.raises(UnauthorizedError): 
        await controller.send_message(msg_req)


async def test_chat_receiver_not_found(db_session_maker):
    """Негативный тест: отправка сообщения несуществующему пользователю"""
    async with db_session_maker() as session:
        user1 = User(login="user1", username="User 1", password_hash="123")
        session.add(user1)
        await session.commit()
        user1_id = user1.id

    ctx = MockServerContext(db_session_maker)
    ctx.user_id = user1_id

    controller = ChatController(ctx)
    security.setup_jwt("secret", "HS256", 1)
    token = security.create_jwt(user1_id, "User 1")

    req = SendMessageRequest(token=token, receiver_id=99999, content="Привет")

    await controller.send_message(req)

    assert ctx.replies[0][0] == "error"

    async with db_session_maker() as session:
        result = await session.execute(select(Message))
        assert result.scalars().all() == []
