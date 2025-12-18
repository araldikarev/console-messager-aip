import jwt
import base64
import datetime

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


# region RSA логика
def generate_rsa_keys():
    """
    Генерирует пару RSA 2048 ключей

    :return: Приватный и публичный ключи.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def public_key_to_pem(public_key) -> bytes:
    """
    Сериализация публичного ключа в PEM формат

    :param public_key: Публичный ключ.
    :return: Ключ в формате PEM.
    :rtype: bytes
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def pem_to_public_key(pem_bytes: bytes):
    """
    Десериализация байт PEM в объект ключа

    :param pem_bytes: PEM байты.
    :type pem_bytes: bytes
    :return: Публичный ключ.
    :rtype: Any
    """
    return serialization.load_pem_public_key(pem_bytes)


def encrypt_rsa(public_key, message: bytes) -> bytes:
    """
    Зашифровывает текст публичным RSA ключом.

    :param public_key: Публичный ключ.
    :param message: Байты сообщений для шифрования.
    :type message: bytes
    :return: Зашифрованные байты сообщения в Base64.
    :rtype: bytes
    """
    ciphered = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(ciphered)


def decrypt_rsa(private_key, b64_ciphered: bytes) -> bytes:
    """
    Расшифровывает Base64 приватным RSA ключом

    :param private_key: Приватный ключ.
    :param b64_ciphered: Зашифрованные байты сообщения в Base64.
    :type b64_ciphered: bytes
    :return: Расшифрованные байты сообщения.
    :rtype: bytes
    """
    raw_ciphered = base64.b64decode(b64_ciphered)
    plain_text = private_key.decrypt(
        raw_ciphered,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return plain_text


# endregion

# region FERNET


def generate_fernet_key() -> bytes:
    """
    Генерирует симметричный ключ Fernet

    :return: Симметричный ключ
    :rtype: bytes
    """
    return Fernet.generate_key()


def encrypt_fernet(fernet: Fernet, data: bytes) -> bytes:
    """
    Шифрует с помощью симметричного ключа.

    :param fernet: Ключ Fernet.
    :type fernet: Fernet
    :param data: Байты для шифрования.
    :type data: bytes
    :return: Зашифрованные байты.
    :rtype: bytes
    """
    return fernet.encrypt(data)


def decrypt_fernet(fernet: Fernet, data: bytes) -> bytes:
    """
    Docstring for decrypt_fernet

    :param fernet: Ключ Fernet.
    :type fernet: Fernet
    :param data: Байты для расшифрования.
    :type data: bytes
    :return: Расшифрованные байты.
    :rtype: bytes
    """
    return fernet.decrypt(data)


# endregion

# region JWT
CONFIG = {
    "JWT_SECRET": "DEFAULT_UNSAFE_SECRET",
    "JWT_ALGORITHM": "HS256",
    "JWT_EXP_HOURS": 24,
}


def setup_jwt(jwt_secret: str, jwt_algo: str, jwt_exp_hours: int):
    """
    Конфигурирует JWT параметры.

    :param jwt_secret: Секрет JWT.
    :type jwt_secret: str
    :param jwt_algo: Алгоритм JWT.
    :type jwt_algo: str
    :param jwt_exp_hours: Время истечения (часы).
    :type jwt_exp_hours: int
    """
    CONFIG["JWT_SECRET"] = jwt_secret
    CONFIG["JWT_ALGORITHM"] = jwt_algo
    CONFIG["JWT_EXP_HOURS"] = jwt_exp_hours


def create_jwt(user_id: int, username: str) -> str:
    """
    Генерирует JWT токен по заданным параметрам.

    :param user_id: ID пользователя.
    :type user_id: int
    :param username: Username пользователя.
    :type username: str
    :return: JWT токен.
    :rtype: str
    """
    payload = {
        "sub": str(user_id),
        "name": str(username),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=CONFIG["JWT_EXP_HOURS"]),
    }

    return jwt.encode(
        payload=payload, key=CONFIG["JWT_SECRET"], algorithm=CONFIG["JWT_ALGORITHM"]
    )


def verify_jwt(token: str) -> dict | None:
    """
    Валидирует JWT ключ.

    :param token: JWT токен
    :type token: str
    :return: Payload JWT токена.
    :rtype: dict | None
    """
    try:
        payload = jwt.decode(
            jwt=token, key=CONFIG["JWT_SECRET"], algorithms=CONFIG["JWT_ALGORITHM"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None


# endregion
