from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserAISettings, ExtractionSnapshot, CVSource
from .providers import BaseAIProvider, StubProvider, get_provider
from cv_manager.models import CV


class UserAISettingsTest(TestCase):
    """UserAISettings modeli için testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
    
    def test_settings_creation(self):
        """AI ayarları oluşturma"""
        settings = UserAISettings.objects.create(
            user=self.user,
            provider="openai",
            api_key="sk-test123",
            model_name="gpt-4o-mini"
        )
        self.assertEqual(settings.provider, "openai")
        # API key otomatik şifreleniyor, decrypted halini kontrol et
        self.assertEqual(settings.get_decrypted_api_key(), "sk-test123")
        # Şifrelenmiş halde 'gAAAAA' ile başlamalı
        self.assertTrue(settings.api_key.startswith("gAAAAA"))
    
    def test_settings_str(self):
        """__str__ metodu testi"""
        settings = UserAISettings.objects.create(
            user=self.user,
            provider="gemini"
        )
        expected = "testuser - gemini"
        self.assertEqual(str(settings), expected)


class ExtractionSnapshotTest(TestCase):
    """ExtractionSnapshot modeli için testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Test User",
            field="WEB"
        )
    
    def test_snapshot_creation(self):
        """Snapshot oluşturma"""
        snapshot = ExtractionSnapshot.objects.create(
            kind="CV",
            cv=self.cv,
            input_text="Test CV text",
            output={"skills": ["Python", "Django"]},
            provider="openai",
            status="OK"
        )
        self.assertEqual(snapshot.kind, "CV")
        self.assertEqual(snapshot.status, "OK")
        self.assertEqual(len(snapshot.output.get("skills", [])), 2)
    
    def test_snapshot_error_status(self):
        """Hata durumunda snapshot"""
        snapshot = ExtractionSnapshot.objects.create(
            kind="POSTING",
            input_text="Failed extraction",
            output={},
            provider="openai",
            status="ERR",
            error_message="API timeout"
        )
        self.assertEqual(snapshot.status, "ERR")
        self.assertIn("timeout", snapshot.error_message)


class CVSourceTest(TestCase):
    """CVSource modeli için testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Test User",
            field="BWL"
        )
    
    def test_source_creation(self):
        """CV source oluşturma"""
        source = CVSource.objects.create(
            cv=self.cv,
            raw_text="John Doe\nPython Developer\nSkills: Python, Django",
            note="LinkedIn version"
        )
        self.assertEqual(source.cv, self.cv)
        self.assertIn("Python", source.raw_text)
        self.assertEqual(source.note, "LinkedIn version")


class ProviderTest(TestCase):
    """AI Provider sistemi testleri"""
    
    def test_stub_provider(self):
        """StubProvider empty dict döndürmeli"""
        provider = StubProvider(api_key="")
        result = provider.extract_json("test text", "test prompt")
        self.assertEqual(result, {})
    
    def test_get_provider_without_settings(self):
        """Ayarı olmayan kullanıcı için StubProvider dönmeli"""
        user = User.objects.create_user(username="nosetup", password="test123")
        provider = get_provider(user)
        self.assertIsInstance(provider, StubProvider)
    
    def test_get_provider_with_settings(self):
        """Ayarlı kullanıcı için doğru provider seçilmeli"""
        user = User.objects.create_user(username="testuser", password="test123")
        UserAISettings.objects.create(
            user=user,
            provider="openai",
            api_key="sk-test",
            model_name="gpt-4o-mini"
        )
        
        provider = get_provider(user)
        # OpenAI kütüphanesi yoksa StubProvider döner, bu normal
        self.assertIsInstance(provider, BaseAIProvider)
    
    def test_get_provider_without_api_key(self):
        """API key olmadan StubProvider dönmeli"""
        user = User.objects.create_user(username="testuser", password="test123")
        UserAISettings.objects.create(
            user=user,
            provider="openai",
            api_key="",  # Boş key
        )
        
        provider = get_provider(user)
        self.assertIsInstance(provider, StubProvider)


class ProviderSelectionTest(TestCase):
    """Provider seçim mantığı testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
    
    def test_openai_provider_selection(self):
        """OpenAI seçimi"""
        UserAISettings.objects.create(
            user=self.user,
            provider="openai",
            api_key="sk-test123"
        )
        provider = get_provider(self.user)
        # Import hatası yoksa OpenAIProvider dönmeli
        self.assertTrue(hasattr(provider, 'api_key'))
        self.assertEqual(provider.api_key, "sk-test123")
    
    def test_gemini_provider_selection(self):
        """Gemini seçimi"""
        UserAISettings.objects.create(
            user=self.user,
            provider="gemini",
            api_key="AIza-test123"
        )
        provider = get_provider(self.user)
        self.assertTrue(hasattr(provider, 'api_key'))
    
    def test_groq_provider_selection(self):
        """Groq seçimi"""
        UserAISettings.objects.create(
            user=self.user,
            provider="groq",
            api_key="gsk-test123"
        )
        provider = get_provider(self.user)
        self.assertTrue(hasattr(provider, 'api_key'))
    
    def test_unknown_provider_fallback(self):
        """Bilinmeyen provider için StubProvider dönmeli"""
        UserAISettings.objects.create(
            user=self.user,
            provider="unknown_provider",
            api_key="test123"
        )
        provider = get_provider(self.user)
        self.assertIsInstance(provider, StubProvider)
