from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from my_health_info.models import HealthInfo


class MyHealthInfoTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.user1_health_info = HealthInfo.objects.create(
            user=self.user1,
            age=20,
            height=170,
            weight=60,
        )

        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword2"
        )

        self.user2_health_info = HealthInfo.objects.create(
            user=self.user2,
            age=25,
            height=175,
            weight=70,
        )

    def test_get_my_health_info_not_authenticated(self):
        """비로그인 유저가 접근할 때 403 에러를 리턴하는지 테스트"""
        response = self.client.get(reverse("my_health_info"))

        self.assertEqual(response.status_code, 403)

    def test_get_my_health_info_user1(self):
        """유저1이 접근할 때 유저1의 건강 정보를 리턴하는지 테스트"""
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("my_health_info"))

        self.assertEqual(response.status_code, 200)

        user1_bmi = self.user1_health_info.weight / (
            (self.user1_health_info.height / 100) ** 2
        )

        self.assertEqual(response.json().get("age"), self.user1_health_info.age)
        self.assertEqual(response.json().get("height"), self.user1_health_info.height)
        self.assertEqual(response.json().get("weight"), self.user1_health_info.weight)
        self.assertEqual(response.json().get("bmi"), user1_bmi)

    def test_get_my_health_info_user2(self):
        """유저2가 접근할 때 유저2의 건강 정보를 리턴하는지 테스트"""
        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.get(reverse("my_health_info"))

        self.assertEqual(response.status_code, 200)

        user2_bmi = self.user2_health_info.weight / (
            (self.user2_health_info.height / 100) ** 2
        )

        self.assertEqual(response.json().get("age"), self.user2_health_info.age)
        self.assertEqual(response.json().get("height"), self.user2_health_info.height)
        self.assertEqual(response.json().get("weight"), self.user2_health_info.weight)
        self.assertEqual(response.json().get("bmi"), user2_bmi)
