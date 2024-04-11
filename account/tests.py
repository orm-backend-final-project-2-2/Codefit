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


class SignUpTestCase(TestCase):
    def setUp(self):
        self.user1 = FakeUser()

    def test_user_can_sign_up(self):
        """
        테스트 회원가입이 성공하는지 확인
        """

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], self.user1.fake_info["username"])
        self.assertEqual(response.data["email"], self.user1.fake_info["email"])

    # def test_sign_up_by_existing_username(self):
    #     """
    #     테스트 이미 존재하는 닉네임일 때 실패하는지 확인
    #     """
    #     self.user1.create_instance()

    #     response = self.client.post(reverse("signup"), data=self.user1.request_create())
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(
    #         response.data["username"][0], "사용자의 닉네임은/는 이미 존재합니다."
    #     )

    # def test_sign_up_by_existing_email(self):
    #     """
    #     테스트 이미 존재하는 이메일일 때 실패하는지 확인
    #     """
    #     self.user1.create_instance()

    #     new_user = FakeUser()
    #     new_user.fake_info["email"] = self.user1.fake_info["email"]

    #     response = self.client.post(reverse("signup"), data=new_user.request_create())
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(
    #         response.data["email"][0], "사용자의 이메일 주소는/은 이미 존재합니다."
    #     )
