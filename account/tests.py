from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from account.models import CustomUser
from utils.fake_data import FakeUser


class LoginTestCase(TestCase):
    def setUp(self):
        self.user1 = FakeUser()
        self.user1.create_instance()

    def test_user_can_login(self):
        """
        테스트 로그인이 성공하는지 확인
        """
        response = self.client.post(reverse("login"), data=self.user1.request_login())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "로그인 성공")

    def test_login_by_unregisterd_user(self):
        """
        테스트 로그인이 등록되지 않은 유저일 때 실패하는지 확인
        """
        new_user = FakeUser()

        response = self.client.post(reverse("login"), data=new_user.request_login())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["message"], "로그인 실패")

    def test_login_by_wrong_password(self):
        """
        테스트 로그인이 비밀번호가 다를 때 실패하는지 확인
        """
        request_login = self.user1.request_login()
        request_login["password"] = "wrong_password"

        response = self.client.post(reverse("login"), data=request_login)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["message"], "로그인 실패")

    def test_login_by_authenticated_user(self):
        """
        로그인 된 유저가 로그인 시도 시 에러 반환
        """
        self.client.force_login(self.user1.instance)

        response = self.client.post(reverse("login"), data=self.user1.request_login())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "로그인 실패")
