import pytest
from pydantic import ValidationError
from dto.models import RegisterRequest, LoginRequest

def test_register_request_valid():
    """Тест: создание корректного пакета регистрации"""
    req = RegisterRequest(
        login="login",
        username="User",
        password_hash="a" * 20
    )
    assert req.action == "register"
    assert req.username == "User"
    assert req.login == "login"

def test_register_request_short_login():
    """Негативный тест: слишком короткий логин"""
    with pytest.raises(ValidationError):
        RegisterRequest(
            login="no", # менее 3 символов
            username="User",
            password_hash="a" * 20
        )

def test_register_request_short_hash():
    """Негативный тест: некорректный хеш пароля"""
    with pytest.raises(ValidationError):
        RegisterRequest(
            login="user",
            username="User",
            password_hash="short" # менее 20 символов
        )

def test_login_request_defaults():
    """Тест: поле action выставляется автоматически"""
    req = LoginRequest(
        login="user123",
        password_hash="b" * 20
    )
    assert req.action == "login"