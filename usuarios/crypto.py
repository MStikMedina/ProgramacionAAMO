from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    key = getattr(settings, 'PASSWORD_ENCRYPT_KEY', None)
    if not key:
        raise ValueError(
            "Falta PASSWORD_ENCRYPT_KEY en settings.py. "
            "Genera una con: from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def cifrar(texto: str) -> str:
    """Devuelve el texto cifrado como string (seguro para guardar en BD)."""
    return _fernet().encrypt(texto.encode()).decode()


def descifrar(cifrado: str) -> str:
    """Descifra y devuelve el texto original. Devuelve '••••••' si falla."""
    try:
        return _fernet().decrypt(cifrado.encode()).decode()
    except (InvalidToken, Exception):
        return '••••••'