# Copyright (c) 2026 Xist.GG LLC

from cryptography.fernet import Fernet

def generate_key() -> str:
    """Generates a URL-safe base64-encoded 32-byte key."""
    return Fernet.generate_key().decode('utf-8')

def encrypt(content: str, key: str) -> bytes:
    """Encrypts content using the provided key."""
    f = Fernet(key.encode('utf-8'))
    return f.encrypt(content.encode('utf-8'))

def decrypt(encrypted_content: bytes, key: str) -> str:
    """Decrypts content using the provided key."""
    f = Fernet(key.encode('utf-8'))
    return f.decrypt(encrypted_content).decode('utf-8')
