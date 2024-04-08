from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from account.models import CustomUser
from faker import Faker


class LoginTestCase(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.user1_info = self.create_fake_user_info()
        self.user1 = CustomUser.objects.create_user(**self.user1_info)

    def create_fake_user_info(self):
        return {
            "email": self.faker.email(),
            "password": self.faker.password(),
            "username": self.faker.user_name(),
        }

    def test_user_can_login(self):
        """
        테스트 로그인이 성공하는지 확인
        """
        response = self.client.post(reverse("login"), data=self.user1_info)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "로그인 성공")

    def test_login_by_unregisterd_user(self):
        """
        테스트 로그인이 등록되지 않은 유저일 때 실패하는지 확인
        """
        new_user_info = self.create_fake_user_info()
        response = self.client.post(reverse("login"), data=new_user_info)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["message"], "로그인 실패")

    def test_login_by_wrong_password(self):
        """
        테스트 로그인이 비밀번호가 다를 때 실패하는지 확인
        """
        new_password = self.faker.password()
        wrong_user_info = {"email": self.user1_info["email"], "password": new_password}
        response = self.client.post(reverse("login"), data=wrong_user_info)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["message"], "로그인 실패")
