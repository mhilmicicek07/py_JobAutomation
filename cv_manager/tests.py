from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import CV, Skill, Experience, Education, Language
from datetime import date


class CVModelTest(TestCase):
    """CV modeli için temel testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Max Mustermann",
            field="WEB",
            email="max@example.com",
            phone="+49 123 456789"
        )
    
    def test_cv_creation(self):
        """CV oluşturma testi"""
        self.assertEqual(self.cv.full_name, "Max Mustermann")
        self.assertEqual(self.cv.field, "WEB")
        self.assertTrue(isinstance(self.cv, CV))
    
    def test_cv_str(self):
        """CV __str__ metodu testi"""
        expected = "Max Mustermann (WEB)"
        self.assertEqual(str(self.cv), expected)


class SkillModelTest(TestCase):
    """Skill modeli için testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Test User",
            field="WEB"
        )
    
    def test_skill_creation(self):
        """Skill oluşturma"""
        skill = Skill.objects.create(cv=self.cv, name="Python", level="advanced")
        self.assertEqual(skill.name, "Python")
        self.assertEqual(skill.level, "advanced")
    
    def test_skill_unique_constraint(self):
        """Aynı CV'de aynı skill'in tekrar eklenemeyeceğini test et"""
        Skill.objects.create(cv=self.cv, name="Django", level="intermediate")
        
        # Aynı isimde ikinci skill oluşturmaya çalış
        with self.assertRaises(Exception):
            Skill.objects.create(cv=self.cv, name="Django", level="advanced")


class ExperienceModelTest(TestCase):
    """Experience modeli için testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(user=self.user, full_name="Test User", field="WEB")
    
    def test_experience_creation(self):
        """Deneyim oluşturma"""
        exp = Experience.objects.create(
            cv=self.cv,
            title="Backend Developer",
            company="Tech GmbH",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            description="Django projelerinde backend geliştirme"
        )
        self.assertEqual(exp.title, "Backend Developer")
        self.assertEqual(exp.company, "Tech GmbH")


class LanguageModelTest(TestCase):
    """Language modeli için testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(user=self.user, full_name="Test User", field="BWL")
    
    def test_language_creation(self):
        """Dil oluşturma"""
        lang = Language.objects.create(cv=self.cv, name="Deutsch", level="C1")
        self.assertEqual(lang.name, "Deutsch")
        self.assertEqual(lang.level, "C1")


class CVViewsTest(TestCase):
    """CV view'ları için testler"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.client.login(username="testuser", password="test123")
        
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Test User",
            field="WEB",
            email="test@example.com"
        )
    
    def test_dashboard_view(self):
        """Dashboard sayfasına erişim testi"""
        response = self.client.get(reverse('cv_manager:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")
    
    def test_cv_detail_view(self):
        """CV detay sayfası testi"""
        response = self.client.get(reverse('cv_manager:cv_detail', args=[self.cv.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cv.full_name)
    
    def test_add_skill_view(self):
        """Skill ekleme testi"""
        response = self.client.post(
            reverse('cv_manager:add_skill', args=[self.cv.pk]),
            {'name': 'Python', 'level': 'advanced'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Skill.objects.filter(cv=self.cv, name='Python').exists())


class CVCRUDTest(TestCase):
    """CV CRUD işlemleri için testler"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.client.login(username="testuser", password="test123")
    
    def test_create_cv(self):
        """CV oluşturma testi"""
        response = self.client.post(reverse('cv_manager:cv_create'), {
            'full_name': 'New User',
            'field': 'BWL',
            'email': 'new@example.com',
            'phone': '0123456789'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CV.objects.filter(full_name='New User').exists())
    
    def test_delete_cv(self):
        """CV silme testi"""
        cv = CV.objects.create(user=self.user, full_name="To Delete", field="GEN")
        response = self.client.post(reverse('cv_manager:cv_delete', args=[cv.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CV.objects.filter(pk=cv.pk).exists())
