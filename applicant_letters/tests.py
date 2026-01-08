from django.test import TestCase
from django.contrib.auth.models import User
from .models import ApplicationDraft
from .services import build_cv_sections, build_cover_letter
from cv_manager.models import CV, Skill, Experience, Education
from job_analyzer.models import JobPosting
from datetime import date


class ApplicationDraftModelTest(TestCase):
    """ApplicationDraft modeli için testler"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(user=self.user, full_name="Test User", field="WEB")
        self.posting = JobPosting.objects.create(
            raw_text="Python Developer gesucht",
            target_field="WEB"
        )
    
    def test_draft_creation(self):
        """Draft oluşturma testi"""
        draft = ApplicationDraft.objects.create(
            posting=self.posting,
            cv=self.cv,
            cover_letter="Test Anschreiben",
            cv_sections={"profil": "Test", "kenntnisse": "Python"},
            language="de"
        )
        self.assertEqual(draft.posting, self.posting)
        self.assertEqual(draft.cv, self.cv)
        self.assertEqual(draft.language, "de")
    
    def test_draft_str(self):
        """__str__ metodu testi"""
        draft = ApplicationDraft.objects.create(
            posting=self.posting,
            cv=self.cv,
            language="de"
        )
        expected_pattern = f"Draft p{self.posting.pk} / cv{self.cv.pk} [de]"
        self.assertEqual(str(draft), expected_pattern)


class BuildCVSectionsTest(TestCase):
    """CV sections oluşturma testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Max Mustermann",
            field="WEB",
            email="max@example.com"
        )
        
        # Skills ekle
        Skill.objects.create(cv=self.cv, name="Python", level="advanced")
        Skill.objects.create(cv=self.cv, name="Django", level="advanced")
        Skill.objects.create(cv=self.cv, name="React", level="intermediate")
        
        # Experience ekle
        Experience.objects.create(
            cv=self.cv,
            title="Backend Developer",
            company="Tech GmbH",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description="Django REST API development"
        )
        
        # Education ekle
        Education.objects.create(
            cv=self.cv,
            degree="Bachelor Computer Science",
            institution="TU Berlin",
            start_date=date(2016, 10, 1),
            end_date=date(2020, 9, 30),
            status="completed"
        )
        
        self.posting = JobPosting.objects.create(
            raw_text="Python Django Developer",
            target_field="WEB",
            extracted_skills=["python", "django", "rest api"]
        )
    
    def test_sections_structure(self):
        """Sections yapısı doğru oluşturulmalı"""
        sections = build_cv_sections(self.cv, self.posting)
        
        self.assertIn("profil", sections)
        self.assertIn("kenntnisse", sections)
        self.assertIn("erfahrung", sections)
        self.assertIn("ausbildung", sections)
        self.assertIn("hinweise", sections)
        self.assertIn("diagnostik", sections)
    
    def test_profil_web_field(self):
        """WEB alanı için profil metni"""
        sections = build_cv_sections(self.cv, self.posting)
        profil = sections["profil"]
        
        self.assertIn("Max Mustermann", profil)
        self.assertIn("Webentwickler", profil)
    
    def test_kenntnisse_section(self):
        """Kenntnisse section'ında skills olmalı"""
        sections = build_cv_sections(self.cv, self.posting)
        kenntnisse = sections["kenntnisse"]
        
        self.assertIn("Python", kenntnisse)
        self.assertIn("Django", kenntnisse)
        self.assertIn("React", kenntnisse)
    
    def test_erfahrung_section(self):
        """Erfahrung section'ında deneyimler olmalı"""
        sections = build_cv_sections(self.cv, self.posting)
        erfahrung = sections["erfahrung"]
        
        self.assertIn("Backend Developer", erfahrung)
        self.assertIn("Tech GmbH", erfahrung)
    
    def test_diagnostik_matched_skills(self):
        """Diagnostik eşleşen skill'leri bulmalı"""
        sections = build_cv_sections(self.cv, self.posting)
        diagnostik = sections["diagnostik"]
        
        matched = diagnostik["matched_skills"]
        self.assertIn("Python", matched)
        self.assertIn("Django", matched)
    
    def test_diagnostik_missing_skills(self):
        """Diagnostik eksik skill'leri tespit etmeli"""
        sections = build_cv_sections(self.cv, self.posting)
        diagnostik = sections["diagnostik"]
        
        missing = diagnostik["missing_skills"]
        self.assertIn("rest api", missing)


class BuildCoverLetterTest(TestCase):
    """Cover letter oluşturma testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Max Mustermann",
            field="WEB"
        )
        
        Skill.objects.create(cv=self.cv, name="Python", level="advanced")
        Skill.objects.create(cv=self.cv, name="Django", level="advanced")
        
        self.posting = JobPosting.objects.create(
            raw_text="Python Django Developer gesucht",
            target_field="WEB",
            extracted_skills=["python", "django"]
        )
    
    def test_cover_letter_generation(self):
        """Cover letter oluşturulmalı"""
        # user=None olduğunda template fallback kullanılır
        letter = build_cover_letter(self.cv, self.posting, user=None)
        
        self.assertIsInstance(letter, str)
        self.assertTrue(len(letter) > 100)
        self.assertIn("Sehr geehrte", letter)
    
    def test_cover_letter_web_field(self):
        """WEB alanı için özel giriş metni"""
        letter = build_cover_letter(self.cv, self.posting, user=None)
        self.assertIn("Webentwicklung", letter)
    
    def test_cover_letter_bwl_field(self):
        """BWL alanı için özel giriş metni"""
        cv_bwl = CV.objects.create(user=self.user, full_name="BWL User", field="BWL")
        posting_bwl = JobPosting.objects.create(
            raw_text="Finanzbuchhalter gesucht",
            target_field="BWL"
        )
        
        letter = build_cover_letter(cv_bwl, posting_bwl, user=None)
        self.assertIn("Finanzbuchhaltung", letter)
    
    def test_cover_letter_includes_skills(self):
        """Cover letter matched skill'leri içermeli"""
        letter = build_cover_letter(self.cv, self.posting, user=None)
        # Template'de matched skill'ler "Schwerpunkte" cümlesinde geçmeli
        self.assertIn("Schwerpunkte", letter)


class CoverLetterFormatTest(TestCase):
    """Cover letter format testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(user=self.user, full_name="Test User", field="GEN")
        self.posting = JobPosting.objects.create(
            raw_text="Generic job posting",
            target_field="GEN"
        )
    
    def test_letter_has_greeting(self):
        """Selamlama bölümü olmalı"""
        letter = build_cover_letter(self.cv, self.posting, user=None)
        self.assertIn("Sehr geehrte Damen und Herren", letter)
    
    def test_letter_has_closing(self):
        """Kapanış bölümü olmalı"""
        letter = build_cover_letter(self.cv, self.posting, user=None)
        self.assertIn("Mit freundlichen Grüßen", letter)
    
    def test_letter_structure(self):
        """Yapı kontrolü (paragraflar)"""
        letter = build_cover_letter(self.cv, self.posting, user=None)
        paragraphs = letter.split("\n\n")
        
        # En az 3 paragraf olmalı (giriş, gövde, kapanış)
        self.assertGreaterEqual(len(paragraphs), 3)
