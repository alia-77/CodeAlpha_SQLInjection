import os
import base64
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SECRET = os.environ.get("VAULT_SECRET", "CodeAlphaSecureVault")

KEY = hashlib.sha256(SECRET.encode()).digest()

aesgcm = AESGCM(KEY)


def encrypt(text: str) -> str:

    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, text.encode(), None)

    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt(text: str) -> str:

    data = base64.urlsafe_b64decode(text.encode())
    nonce = data[:12]
    ciphertext = data[12:]

    return aesgcm.decrypt(nonce, ciphertext, None).decode()