from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class UserAuthenticationTest(TestCase):
    """Kullanıcı authentication testleri"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        """Login sayfası GET isteği"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Giriş Yap')
    
    def test_login_success(self):
        """Başarılı login"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_fail(self):
        """Başarısız login"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout(self):
        """Logout işlemi"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
    
    def test_register_view_get(self):
        """Register sayfası GET isteği"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kayıt Ol')
    
    def test_register_success(self):
        """Başarılı kayıt"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())
