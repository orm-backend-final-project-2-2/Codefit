from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from my_health_info.models import HealthInfo
from freezegun import freeze_time
from faker import Faker


class MyHealthInfoTestCase(TestCase):
    def setUp(self):
        self.fake = Faker()

        self.user1 = self.create_fake_user()
        self.user1_health_info = self.create_fake_health_info(self.user1)
        self.user1_bmi = self.calculate_users_bmi(self.user1_health_info)

        self.user2 = self.create_fake_user()
        self.user2_health_info = self.create_fake_health_info(self.user2)

    def create_fake_user(self):
        fake_user_info = {
            "username": self.fake.user_name(),
            "password": self.fake.password(),
        }

        User.objects.create_user(**fake_user_info)
        return fake_user_info

    def create_fake_health_info(self, user):
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
        return health_info.get("weight") / ((health_info.get("height") / 100) ** 2)

    def test_get_my_health_info_not_authenticated(self):
        """비로그인 유저가 접근할 때 403 에러를 리턴하는지 테스트"""
        response = self.client.get(reverse("my_health_info"))

        self.assertEqual(response.status_code, 403)

    def test_get_my_health_info_user1(self):
        """유저1이 접근할 때 유저1의 건강 정보를 리턴하는지 테스트"""
        self.client.login(
            username=self.user1.get("username"), password=self.user1.get("password")
        )
        response = self.client.get(reverse("my_health_info"))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json().get("age"), self.user1_health_info.get("age"))
        self.assertEqual(
            response.json().get("height"), self.user1_health_info.get("height")
        )
        self.assertEqual(
            response.json().get("weight"), self.user1_health_info.get("weight")
        )
        self.assertEqual(response.json().get("bmi"), self.user1_bmi)

    def test_get_my_health_info_user2(self):
        """유저2가 접근할 때 유저2의 건강 정보를 리턴하는지 테스트"""
        self.client.login(
            username=self.user2.get("username"), password=self.user2.get("password")
        )
        response = self.client.get(reverse("my_health_info"))

        self.assertEqual(response.status_code, 200)

        user2_bmi = self.calculate_users_bmi(self.user2_health_info)

        self.assertEqual(response.json().get("age"), self.user2_health_info.get("age"))
        self.assertEqual(
            response.json().get("height"), self.user2_health_info.get("height")
        )
        self.assertEqual(
            response.json().get("weight"), self.user2_health_info.get("weight")
        )
        self.assertEqual(response.json().get("bmi"), user2_bmi)

    @freeze_time("2023-01-01")
    def test_get_my_health_info_last(self):
        """접근 시 마지막으로 생성된 건강 정보를 리턴하는지 테스트"""
        new_health_info = self.create_fake_health_info(self.user1)

        self.client.login(
            username=self.user1.get("username"), password=self.user1.get("password")
        )

        response = self.client.get(reverse("my_health_info_last"))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json().get("age"), self.user1_health_info.get("age"))
        self.assertEqual(
            response.json().get("height"), self.user1_health_info.get("height")
        )
        self.assertEqual(
            response.json().get("weight"), self.user1_health_info.get("weight")
        )
        self.assertEqual(response.json().get("bmi"), self.user1_bmi)

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

        self.assertEqual(data.get("age"), new_health_info["age"])
        self.assertEqual(data.get("height"), new_health_info["height"])
        self.assertEqual(data.get("weight"), new_health_info["weight"])
        self.assertEqual(
            data.get("bmi"),
            new_health_info["weight"] / ((new_health_info["height"] / 100) ** 2),
        )

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
