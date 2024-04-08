from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from account.models import CustomUser


class LoginTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpassword", nickname="testuser"
        )

    def test_user_can_login(self):
        """
        테스트 로그인이 성공하는지 확인
        """
        data = {"email": "test@example.com", "password": "testpassword"}
        response = self.client.post(
            reverse("login"),
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "로그인 성공")
