from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from my_health_info.models import HealthInfo
from freezegun import freeze_time
from faker import Faker
from datetime import datetime, timedelta


class MyHealthInfoTestCase(TestCase):
    def setUp(self):
        """초기설정"""
        self.fake = Faker()

        self.user1 = self.create_fake_user()
        self.user1_health_info = self.create_fake_health_info(self.user1)
        self.user1_bmi = self.calculate_users_bmi(self.user1_health_info)

    def create_fake_user(self):
        """가짜 유저 생성"""
        fake_user_info = {
            "username": self.fake.user_name(),
            "password": self.fake.password(),
        }

        User.objects.create_user(**fake_user_info)
        return fake_user_info

    def create_fake_health_info(self, user):
        """가짜 건강 정보 생성"""
        fake_health_info = {
            "user": User.objects.get(username=user["username"]),
            "age": self.fake.random_int(min=1, max=70),
            "height": self.fake.random_int(min=100, max=200),
            "weight": self.fake.random_int(min=30, max=150),
        }

        HealthInfo.objects.create(
            **fake_health_info,
        )

        return fake_health_info

    def calculate_users_bmi(self, health_info):
        """BMI 계산"""
        return health_info.get("weight") / ((health_info.get("height") / 100) ** 2)

    def assert_equal_health_info(self, health_info, expected_health_info):
        """건강 정보 비교"""
        self.assertEqual(health_info.get("age"), expected_health_info.get("age"))
        self.assertEqual(health_info.get("height"), expected_health_info.get("height"))
        self.assertEqual(health_info.get("weight"), expected_health_info.get("weight"))
        self.assertEqual(
            health_info.get("bmi"), self.calculate_users_bmi(expected_health_info)
        )

    def test_get_my_health_info_not_authenticated(self):
        """비로그인 유저가 접근할 때 403 에러를 리턴하는지 테스트"""
        response = self.client.get(reverse("my_health_info"))

        self.assertEqual(response.status_code, 403)

    def test_get_my_health_info_last_30_days(self):
        self.client.login(
            username=self.user1.get("username"), password=self.user1.get("password")
        )

        now = datetime.now()
        for days_back in range(120, -1, -1):
            past_day = now - timedelta(days=days_back)
            with freeze_time(f"{past_day.strftime('%Y-%m-%d')}"):
                new_health_info = self.create_fake_health_info(self.user1)

        self.client.get(reverse("my_health_info"))

    @freeze_time("2025-01-01")
    def test_reject_post_my_health_info_if_same_day(self):
        """POST 요청으로 같은 날짜에 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        new_user = self.create_fake_user()
        new_health_info = self.create_fake_health_info(new_user)

        response_1 = self.client.post(reverse("my_health_info"))
        response_2 = self.client.post(reverse("my_health_info"))

        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_2.status_code, 400)

    @freeze_time("2023-01-01")
    def test_get_my_health_info_last(self):
        """접근 시 마지막으로 생성된 건강 정보를 리턴하는지 테스트"""
        new_health_info = self.create_fake_health_info(self.user1)

        self.client.login(
            username=self.user1.get("username"), password=self.user1.get("password")
        )

        response = self.client.get(reverse("my_health_info_last"))

        self.assertEqual(response.status_code, 200)

        self.assert_equal_health_info(response.json(), self.user1_health_info)

    def test_post_my_health_info(self):
        """POST 요청으로 건강 정보를 생성하는지 테스트"""
        self.client.login(
            username=self.user1.get("username"), password=self.user1.get("password")
        )

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

        self.assert_equal_health_info(data, new_health_info)

    def test_post_my_health_info_with_invalid_age(self):
        """POST 요청으로 나이가 음수인 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        self.client.login(
            username=self.user1.get("username"), password=self.user1.get("password")
        )

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
