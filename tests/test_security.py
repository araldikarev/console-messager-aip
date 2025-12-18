import jwt
import datetime
import pytest

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.primitives.asymmetric import rsa

import security


# region RSA Тесты
def test_rsa_keys_generation():
    """Тест: ключи генерируются"""
    private, public = security.generate_rsa_keys()
    assert private is not None
    assert public is not None
    assert private.key_size == 2048


def test_rsa_encryption_and_decryption():
    """Тест: зашифровка и расшифровка"""
    private, public = security.generate_rsa_keys()
    original_message = b"Secret Message 123"

    encrypted = security.encrypt_rsa(public, original_message)
    assert encrypted != original_message

    decrypted = security.decrypt_rsa(private, encrypted)
    assert decrypted == original_message


def test_rsa_decrypt_with_wrong_private_key_raises():
    """Негативный тест: расшифровка чужим ключом вызывает ошибку"""
    _, public_1 = security.generate_rsa_keys()
    private_2, _ = security.generate_rsa_keys()

    encrypted = security.encrypt_rsa(public_1, b"hello")

    with pytest.raises(Exception):
        security.decrypt_rsa(private_2, encrypted)


def test_rsa_encrypt_too_long_message_raises():
    """Негативный тест: слишком длинное сообщение для RSA 2048"""
    _, public_key = security.generate_rsa_keys()
    message = b"a" * 1000

    with pytest.raises(Exception):
        security.encrypt_rsa(public_key, message)


def test_rsa_keys_generation_failure(monkeypatch):
    """Негативный тест: Падение generate_rsa_keys"""

    def fail(*args, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(rsa, "generate_private_key", fail)

    with pytest.raises(RuntimeError):
        security.generate_rsa_keys()


# endregion


# region Fernet Тесты
def test_fernet_encryption_and_decryption():
    """Тест: симметричное шифрование"""
    key = security.generate_fernet_key()
    cipher = Fernet(key)

    message = b"Hello World"
    encrypted = cipher.encrypt(message)
    decrypted = cipher.decrypt(encrypted)
    assert message == decrypted


def test_fernet_decrypt_wrong_key_fails():
    """Негативный тест: расшифровка Fernet неверным ключом"""
    key1 = security.generate_fernet_key()
    key2 = security.generate_fernet_key()
    cipher1 = Fernet(key1)
    cipher2 = Fernet(key2)

    token = cipher1.encrypt(b"data")

    with pytest.raises(InvalidToken):
        cipher2.decrypt(token)


# endregion


# region JWT Тесты
def test_jwt_success():
    """Тест: создание и проверка токена"""
    security.setup_jwt("super_secret", "HS256", 1)

    token = security.create_jwt(user_id=55, username="test_user")
    assert isinstance(token, str)

    payload = security.verify_jwt(token)
    assert payload is not None
    assert payload["sub"] == "55"
    assert payload["name"] == "test_user"


def test_jwt_invalid():
    """Негативный тест: подделка подписи"""
    security.setup_jwt("secret_A", "HS256", 1)
    token = security.create_jwt(1, "User")

    security.setup_jwt("secret_B", "HS256", 1)
    payload = security.verify_jwt(token)
    assert payload is None


def test_jwt_expired():
    """Негативный тест: истёкший срок JWT"""
    secret = "secret"
    algo = "HS256"
    security.setup_jwt(secret, algo, 1)

    payload = {
        "sub": "123",
        "name": "User",
        "exp": datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(hours=1),
    }
    expired_token = jwt.encode(payload, secret, algorithm=algo)

    result = security.verify_jwt(expired_token)
    assert result is None


def test_jwt_malformed_token_returns_none():
    """Негативный тест: некорретный (формат) токен"""
    security.setup_jwt("secret", "HS256", 1)
    assert security.verify_jwt("not-a-jwt") is None


# endregion
