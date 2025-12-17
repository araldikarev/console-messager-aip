import pytest
import security
from cryptography.fernet import Fernet

#region RSA Тесты
def test_rsa_keys_generation():
    """
    Тест: ключи генерируются
    """
    private, public = security.generate_rsa_keys()
    assert private is not None
    assert public is not None
    assert private.key_size == 2048

def test_rsa_encryption_and_decryption():
    """
    Тест: зашифровка и расшифровка
    """
    private, public = security.generate_rsa_keys()
    original_message = b"Secret Message 123"
    
    encrypted = security.encrypt_rsa(public, original_message)
    assert encrypted != original_message
    
    decrypted = security.decrypt_rsa(private, encrypted)
    assert decrypted == original_message
#endregion

#region Fernet Тесты
def test_fernet_encryption_and_decryption():
    """
    Тест: симметричное шифрование
    """
    key = security.generate_fernet_key()
    cipher = Fernet(key)
    
    message = b"Hello World"
    encrypted = cipher.encrypt(message)
    decrypted = cipher.decrypt(encrypted)
    assert message == decrypted
#endregion

#region JWT Тесты
def test_jwt_success():
    """
    Тест: создание и проверка токена
    """
    security.setup_jwt("super_secret", "HS256", 1)
    
    token = security.create_jwt(user_id=55, username="test_user")
    assert isinstance(token, str)
    
    payload = security.verify_jwt(token)
    assert payload is not None
    assert payload["sub"] == "55"
    assert payload["name"] == "test_user"

def test_jwt_invalid():
    """
    Негативный тест: подделка подписи
    """
    security.setup_jwt("secret_A", "HS256", 1)
    token = security.create_jwt(1, "User")
    
    security.setup_jwt("secret_B", "HS256", 1)
    payload = security.verify_jwt(token)
    assert payload is None
#endregion