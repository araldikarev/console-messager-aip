import base64
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