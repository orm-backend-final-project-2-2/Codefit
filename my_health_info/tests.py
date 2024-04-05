from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from my_health_info.models import HealthInfo
from freezegun import freeze_time


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

        self.user1_bmi = self.user1_health_info.weight / (
            (self.user1_health_info.height / 100) ** 2
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

        self.assertEqual(response.json().get("age"), self.user1_health_info.age)
        self.assertEqual(response.json().get("height"), self.user1_health_info.height)
        self.assertEqual(response.json().get("weight"), self.user1_health_info.weight)
        self.assertEqual(response.json().get("bmi"), self.user1_bmi)

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

    @freeze_time("2023-01-01")
    def test_get_my_health_info_last(self):
        """접근 시 마지막으로 생성된 건강 정보를 리턴하는지 테스트"""
        HealthInfo.objects.create(
            user=self.user1,
            age=19,
            height=175,
            weight=50,
        )

        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("my_health_info_last"))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json().get("age"), self.user1_health_info.age)
        self.assertEqual(response.json().get("height"), self.user1_health_info.height)
        self.assertEqual(response.json().get("weight"), self.user1_health_info.weight)
        self.assertEqual(response.json().get("bmi"), self.user1_bmi)

    def test_post_my_health_info(self):
        """POST 요청으로 건강 정보를 생성하는지 테스트"""
        self.client.login(username="testuser", password="testpassword")

        new_health_info = {
            "age": 21,
            "height": 180,
            "weight": 70,
        }

        response = self.client.post(
            reverse("my_health_info"),
            data=new_health_info,
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()

        self.assertEqual(data.get("age"), new_health_info["age"])
        self.assertEqual(data.get("height"), new_health_info["height"])
        self.assertEqual(data.get("weight"), new_health_info["weight"])
        self.assertEqual(
            data.get("bmi"),
            new_health_info["weight"] / ((new_health_info["height"] / 100) ** 2),
        )

    def test_post_my_health_info_with_invalid_age(self):
        """POST 요청으로 나이가 음수인 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        self.client.login(username="testuser", password="testpassword")

        new_health_info = {
            "age": -1,
            "height": 180,
            "weight": 70,
        }

        response = self.client.post(
            reverse("my_health_info"),
            data=new_health_info,
        )

        self.assertEqual(response.status_code, 400)
