import jwt
import base64
import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

#region RSA логика
def generate_rsa_keys():
    """Генерирует пару RSA 2048 ключей"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def public_key_to_pem(public_key) -> bytes:
    """Сериализация публичного ключа в PEM формат"""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def pem_to_public_key(pem_bytes: bytes):
    """Десериализация байт PEM в объект ключа"""
    return serialization.load_pem_public_key(pem_bytes)

def encrypt_rsa(public_key, message: bytes) -> bytes:
    """Зашифровывает текст публичным RSA ключом"""
    ciphered = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(ciphered)

def decrypt_rsa(private_key, b64_ciphered: bytes) -> bytes:
    """Расшифровывает Base64 приватным RSA ключом"""
    raw_ciphered = base64.b64decode(b64_ciphered)
    plain_text = private_key.decrypt(
        raw_ciphered,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plain_text
#endregion

#region FERNET

def generate_fernet_key() -> bytes:
    return Fernet.generate_key()

def encrypt_fernet(fernet: Fernet, data: bytes) -> bytes:
    return fernet.encrypt(data)

def decrypt_fernet(fernet: Fernet, data: bytes) -> bytes:
    return fernet.decrypt(data)

#endregion

#region JWT
JWT_SECRET = "RANDOM_SUPER_ULTRA_SECRET_KEY_3000_JUST_AS_TEMPLATE!"
JWT_ALGORITHM = "HS256"

def create_jwt(user_id: int, username: str) -> str:
    """Генерирует JWT токен, который живет 24 часа"""
    payload = {
        "sub": str(user_id),
        "name": str(username),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }

    return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(jwt=token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
#endregion