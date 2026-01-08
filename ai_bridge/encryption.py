"""
API Key şifreleme/çözme yardımcı fonksiyonları.
Django SECRET_KEY kullanarak Fernet encryption uygular.
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings


def _get_fernet_key() -> bytes:
    """
    Django SECRET_KEY'den Fernet uyumlu 32-byte key türet.
    """
    secret = settings.SECRET_KEY.encode()
    # SHA-256 hash alıp base64'e çevir (Fernet için gerekli format)
    digest = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_api_key(plain_text: str) -> str:
    """
    API key'i şifreler ve string olarak döner.
    """
    if not plain_text:
        return ""
    
    try:
        fernet = Fernet(_get_fernet_key())
        encrypted_bytes = fernet.encrypt(plain_text.encode())
        return encrypted_bytes.decode()
    except Exception as e:
        # Şifreleme başarısız olursa log atıp plain text döndür
        # (Production'da daha iyi hata yönetimi yapılmalı)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Encryption failed: {e}")
        return plain_text


def decrypt_api_key(encrypted_text: str) -> str:
    """
    Şifrelenmiş API key'i çözer ve plain text döner.
    """
    if not encrypted_text:
        return ""
    
    try:
        fernet = Fernet(_get_fernet_key())
        decrypted_bytes = fernet.decrypt(encrypted_text.encode())
        return decrypted_bytes.decode()
    except Exception as e:
        # Decryption başarısız (eski format olabilir), plain text olarak dön
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Decryption failed, returning as-is: {e}")
        return encrypted_text
