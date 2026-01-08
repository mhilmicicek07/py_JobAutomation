import json
import logging
from abc import ABC, abstractmethod

# OpenAI kütüphanesi yüklü değilse hata vermesin, çalışma zamanında kontrol edelim
try:
    from openai import OpenAI, OpenAIError
except ImportError:
    OpenAI = None
    OpenAIError = None

# Google Gemini
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Groq
try:
    from groq import Groq
except ImportError:
    Groq = None

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

class GeminiProvider(BaseAIProvider):
    """
    Google Gemini AI sağlayıcısı.
    """
    def extract_json(self, text: str, system_prompt: str) -> dict:
        if not genai:
            raise RuntimeError("Google Generative AI kütüphanesi yüklü değil. 'pip install google-generativeai' çalıştırın.")
        
        if not self.api_key:
            raise ValueError("Gemini API Key eksik.")

        try:
            genai.configure(api_key=self.api_key)
            model_name = self.model_name if self.model_name else "gemini-1.5-flash"
            model = genai.GenerativeModel(model_name)
            
            # Gemini için prompt birleştirme
            full_prompt = f"{system_prompt}\n\nLütfen aşağıdaki metni analiz et ve JSON formatında yanıt ver:\n\n{text}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini API Hatası: {e}")
            raise e


class GroqProvider(BaseAIProvider):
    """
    Groq AI sağlayıcısı (Llama3, Mixtral vs.)
    """
    def extract_json(self, text: str, system_prompt: str) -> dict:
        if not Groq:
            raise RuntimeError("Groq kütüphanesi yüklü değil. 'pip install groq' çalıştırın.")
        
        if not self.api_key:
            raise ValueError("Groq API Key eksik.")

        try:
            client = Groq(api_key=self.api_key)
            model = self.model_name if self.model_name else "llama-3.3-70b-versatile"
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\nYANITINI SADECE GEÇERLİ JSON FORMATINDA VER!"},
                    {"role": "user", "content": text},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            return json.loads(content) # type: ignore
        except Exception as e:
            logger.error(f"Groq API Hatası: {e}")
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
    API key'leri otomatik olarak decrypt eder.
    """
    # Kullanıcının ayarları var mı?
    if not hasattr(user, "ai_settings"):
        return StubProvider(api_key="")

    settings = user.ai_settings
    if not settings.api_key:
        return StubProvider(api_key="")

    # API key'i decrypt et
    decrypted_key = settings.get_decrypted_api_key()
    provider_name = settings.provider.lower()
    
    if provider_name == "openai":
        return OpenAIProvider(
            api_key=decrypted_key, 
            model_name=settings.model_name
        )
    elif provider_name == "gemini":
        return GeminiProvider(
            api_key=decrypted_key,
            model_name=settings.model_name
        )
    elif provider_name == "groq":
        return GroqProvider(
            api_key=decrypted_key,
            model_name=settings.model_name
        )
    
    logger.warning(f"Bilinmeyen provider: {provider_name}. StubProvider kullanılıyor.")
    return StubProvider(api_key="")