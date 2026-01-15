from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="imran", password="1234")

    def test_login(self):
        response = self.client.post("/api/token/", {"username": "imran", "password": "1234"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
