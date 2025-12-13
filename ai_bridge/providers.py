import json
import logging
from abc import ABC, abstractmethod

# OpenAI kütüphanesi yüklü değilse hata vermesin, çalışma zamanında kontrol edelim
try:
    from openai import OpenAI, OpenAIError
except ImportError:
    OpenAI = None
    OpenAIError = None

logger = logging.getLogger(__name__)

class BaseAIProvider(ABC):
    """
    Tüm AI sağlayıcıları bu temel sınıftan türetilecek.
    """
    def __init__(self, api_key, model_name=None):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def extract_json(self, text: str, system_prompt: str) -> dict:
        """
        Verilen metni ve sistem talimatını alıp, JSON formatında yanıt döndürmeli.
        """
        pass

class OpenAIProvider(BaseAIProvider):
    def extract_json(self, text: str, system_prompt: str) -> dict:
        if not OpenAI:
            raise RuntimeError("OpenAI kütüphanesi yüklü değil. 'pip install openai' çalıştırın.")
        
        if not self.api_key:
            raise ValueError("OpenAI API Key eksik.")

        client = OpenAI(api_key=self.api_key)
        # Kullanıcı özel model seçmediyse varsayılanı kullan
        model = self.model_name if self.model_name else "gpt-4o-mini"

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},  # JSON modunu zorla
                temperature=0.2,
            )
            content = response.choices[0].message.content
            return json.loads(content) # type: ignore
        except Exception as e:
            logger.error(f"OpenAI API Hatası: {e}")
            raise e

class StubProvider(BaseAIProvider):
    """
    API Key girilmediyse veya test amaçlı kullanılan 'kör' sağlayıcı.
    """
    def extract_json(self, text: str, system_prompt: str) -> dict:
        logger.warning("StubProvider kullanılıyor (Gerçek AI çağrısı yapılmadı).")
        return {}

def get_provider(user) -> BaseAIProvider:
    """
    Verilen Django kullanıcısının (User) ayarlarına göre uygun Provider nesnesini döndürür.
    """
    # Kullanıcının ayarları var mı?
    if not hasattr(user, "ai_settings"):
        return StubProvider(api_key="")

    settings = user.ai_settings
    if not settings.api_key:
        return StubProvider(api_key="")

    if settings.provider == "openai":
        return OpenAIProvider(
            api_key=settings.api_key, 
            model_name=settings.model_name
        )
    
    # İleride "gemini" veya "groq" buraya eklenecek
    
    return StubProvider(api_key="")