from django.test import TestCase
from django.contrib.auth.models import User
from .models import JobPosting
from .services import extract_requirements, score_posting_against_cv, decision_from_score, get_primary_cv_or_fallback
from cv_manager.models import CV, Skill


class JobPostingModelTest(TestCase):
    """JobPosting modeli için testler"""
    
    def setUp(self):
        self.posting = JobPosting.objects.create(
            raw_text="Wir suchen einen Python Developer mit Django und REST API Erfahrung.",
            target_field="WEB"
        )
    
    def test_posting_creation(self):
        """İlan oluşturma testi"""
        self.assertEqual(self.posting.target_field, "WEB")
        self.assertTrue(isinstance(self.posting, JobPosting))
    
    def test_posting_default_values(self):
        """Varsayılan değerlerin doğru olduğunu test et"""
        self.assertEqual(self.posting.extracted_skills, [])
        self.assertEqual(self.posting.extracted_experience, [])
        self.assertIsNone(self.posting.match_score)
        self.assertIsNone(self.posting.decision)


class ExtractRequirementsTest(TestCase):
    """İlan analizi servisi için testler"""
    
    def test_extract_web_skills(self):
        """Web alanı için skill çıkarımı"""
        text = "Wir suchen einen Entwickler mit Python, Django, REST API und PostgreSQL Kenntnissen."
        result = extract_requirements(text, "WEB")
        
        skills = result.get("skills", [])
        self.assertIn("python", skills)
        self.assertIn("django", skills)
        self.assertIn("rest api", skills)
        self.assertIn("postgresql", skills)
    
    def test_extract_bwl_skills(self):
        """BWL alanı için skill çıkarımı"""
        text = "Kenntnisse in SAP FI, Kreditorenbuchhaltung, DATEV und Excel erforderlich."
        result = extract_requirements(text, "BWL")
        
        skills = result.get("skills", [])
        self.assertIn("sap", skills)
        self.assertIn("sap fi", skills)
        self.assertIn("datev", skills)
        self.assertIn("excel", skills)
    
    def test_extract_with_empty_text(self):
        """Boş metin için çıkarım testi"""
        result = extract_requirements("", "WEB")
        self.assertEqual(result.get("skills", []), [])
    
    def test_skill_canonicalization(self):
        """Eşanlamlı skill'lerin birleştirilmesi"""
        text = "REST API and API development experience required."
        result = extract_requirements(text, "WEB")
        skills = result.get("skills", [])
        
        # "rest api", "rest", "api" hepsi "rest api" olarak birleşmeli
        self.assertIn("rest api", skills)


class ScoringTest(TestCase):
    """Skor hesaplama testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.cv = CV.objects.create(
            user=self.user,
            full_name="Test Developer",
            field="WEB"
        )
        
        # CV'ye skill'ler ekle
        Skill.objects.create(cv=self.cv, name="Python", level="advanced")
        Skill.objects.create(cv=self.cv, name="Django", level="advanced")
        Skill.objects.create(cv=self.cv, name="REST API", level="intermediate")
        Skill.objects.create(cv=self.cv, name="PostgreSQL", level="intermediate")
    
    def test_perfect_match(self):
        """Tam eşleşme skoru"""
        skills_needed = ["python", "django", "rest api", "postgresql"]
        score = score_posting_against_cv(self.cv, skills_needed)
        self.assertEqual(score, 100)
    
    def test_partial_match(self):
        """Kısmi eşleşme skoru"""
        skills_needed = ["python", "django", "react", "typescript"]
        score = score_posting_against_cv(self.cv, skills_needed)
        self.assertEqual(score, 50)  # 2/4 = 50%
    
    def test_no_match(self):
        """Hiç eşleşmeyen durumda skor 0 olmalı"""
        skills_needed = ["java", "spring", "kotlin"]
        score = score_posting_against_cv(self.cv, skills_needed)
        self.assertEqual(score, 0)
    
    def test_empty_skills_needed(self):
        """Gerekli skill listesi boşsa skor 0 olmalı"""
        score = score_posting_against_cv(self.cv, [])
        self.assertEqual(score, 0)


class DecisionTest(TestCase):
    """Karar verme algoritması testleri"""
    
    def test_apply_decision(self):
        """Yüksek skor APPLY döndürmeli"""
        self.assertEqual(decision_from_score(85), "APPLY")
        self.assertEqual(decision_from_score(100), "APPLY")
    
    def test_review_decision(self):
        """Orta skor REVIEW döndürmeli"""
        self.assertEqual(decision_from_score(50), "REVIEW")
        self.assertEqual(decision_from_score(75), "REVIEW")
    
    def test_skip_decision(self):
        """Düşük skor SKIP döndürmeli"""
        self.assertEqual(decision_from_score(30), "SKIP")
        self.assertEqual(decision_from_score(0), "SKIP")
    
    def test_none_score(self):
        """None skor REVIEW döndürmeli"""
        self.assertEqual(decision_from_score(None), "REVIEW")


class GetPrimaryCVTest(TestCase):
    """Primary CV seçimi testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
    
    def test_get_primary_cv(self):
        """is_primary=True olan CV seçilmeli"""
        cv1 = CV.objects.create(user=self.user, full_name="CV 1", field="WEB", is_primary=False)
        cv2 = CV.objects.create(user=self.user, full_name="CV 2", field="WEB", is_primary=True)
        
        result = get_primary_cv_or_fallback("WEB")
        self.assertEqual(result.pk, cv2.pk)
    
    def test_fallback_to_field(self):
        """Primary yoksa field eşleşen herhangi biri seçilmeli"""
        cv = CV.objects.create(user=self.user, full_name="CV 1", field="BWL", is_primary=False)
        
        result = get_primary_cv_or_fallback("BWL")
        self.assertEqual(result.pk, cv.pk)
    
    def test_fallback_to_gen(self):
        """Hiçbir eşleşme yoksa GEN alanı seçilmeli"""
        cv_gen = CV.objects.create(user=self.user, full_name="General CV", field="GEN")
        cv_web = CV.objects.create(user=self.user, full_name="Web CV", field="WEB")
        
        result = get_primary_cv_or_fallback("BWL")
        self.assertEqual(result.field, "GEN")
