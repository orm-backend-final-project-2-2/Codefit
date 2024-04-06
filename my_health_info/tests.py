from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from my_health_info.models import HealthInfo
from freezegun import freeze_time
from faker import Faker
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status


class MyHealthInfoTestCase(TestCase):
    @freeze_time("2020-01-01")
    def setUp(self):
        """초기설정"""
        self.fake = Faker()

        self.user1_info = self.create_fake_user_info()
        self.user1 = User.objects.create_user(**self.user1_info)

        self.user1_health_info = self.create_fake_health_info_request()
        HealthInfo.objects.create(user=self.user1, **self.user1_health_info)

    def calculate_users_bmi(self, health_info):
        """BMI 계산"""
        return health_info.get("weight") / ((health_info.get("height") / 100) ** 2)

    def create_fake_user_info(self):
        """가짜 유저 정보를 생성하는 함수"""

        return {
            "username": self.fake.user_name(),
            "password": self.fake.password(),
        }

    def create_fake_health_info_request(self):
        """가짜 건강 정보를 생성하는 함수"""

        return {
            "age": self.fake.random_int(min=20, max=80),
            "height": self.fake.random_int(min=150, max=200),
            "weight": self.fake.random_int(min=50, max=100),
        }

    def assert_equal_health_info(self, health_info, expected_health_info):
        """건강 정보 비교"""

        self.assertEqual(health_info.get("age"), expected_health_info.get("age"))
        self.assertEqual(health_info.get("height"), expected_health_info.get("height"))
        self.assertEqual(health_info.get("weight"), expected_health_info.get("weight"))
        self.assertEqual(
            health_info.get("bmi"), self.calculate_users_bmi(expected_health_info)
        )

    def test_get_my_health_info_not_authenticated(self):
        """비로그인 유저가 my-helath-info/에 접근할 때 403 에러를 리턴하는지 테스트"""
        new_health_info = self.create_fake_health_info_request()

        responses = {
            "list": self.client.get(reverse("my-health-info-list")),
            "create": self.client.post(
                reverse("my-health-info-list"),
                data=new_health_info,
                content_type="application/json",
            ),
            "retrieve": self.client.get(
                reverse("my-health-info-detail", kwargs={"pk": 1})
            ),
            "put": self.client.put(
                reverse("my-health-info-detail", kwargs={"pk": 1}),
                data=new_health_info,
                content_type="application/json",
            ),
            "patch": self.client.patch(
                reverse("my-health-info-detail", kwargs={"pk": 1}),
                data=new_health_info,
                content_type="application/json",
            ),
            "delete": self.client.delete(
                reverse("my-health-info-detail", kwargs={"pk": 1})
            ),
            "last": self.client.get(reverse("my-health-info-last")),
        }

        for action, response in responses.items():
            with self.subTest(action=action):
                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                    f"{action} did not return 403",
                )

    def test_get_my_health_info_last_30_days(self):
        """로그인한 유저가 my-health-info-list에 접근할 때 최근 35일간의 건강 정보를 리턴하는지 테스트"""
        new_user_info = self.create_fake_user_info()
        new_user = User.objects.create_user(**new_user_info)

        self.client.force_login(new_user)

        now = timezone.now()
        for days_back in range(40, -1, -1):
            past_day = now - timedelta(days=days_back)
            with freeze_time(f"{past_day.strftime('%Y-%m-%d')}"):
                new_health_info = self.create_fake_health_info_request()
                HealthInfo.objects.create(user=new_user, **new_health_info)

        response = self.client.get(reverse("my-health-info-list"))
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(data), 35)

    def test_post_my_health_info(self):
        """POST 요청으로 건강 정보를 생성하는지 테스트"""
        self.client.force_login(self.user1)

        new_health_info = self.create_fake_health_info_request()

        response = self.client.post(
            reverse("my-health-info-list"),
            data=new_health_info,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assert_equal_health_info(data, new_health_info)

    @freeze_time("2025-01-01")
    def test_reject_post_my_health_info_if_same_day(self):
        """POST 요청으로 같은 날짜에 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        new_user_info = self.create_fake_user_info()
        new_user = User.objects.create_user(**new_user_info)

        new_health_info = self.create_fake_health_info_request()

        self.client.force_login(new_user)

        response_1 = self.client.post(
            reverse("my-health-info-list"), data=new_health_info
        )
        response_2 = self.client.post(
            reverse("my-health-info-list"), data=new_health_info
        )

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_my_health_info_last(self):
        """GET 요청으로 가장 최근 생성된 건강 정보를 조회하는지 테스트"""
        new_health_info = self.create_fake_health_info_request()
        HealthInfo.objects.create(user=self.user1, **new_health_info)

        self.client.force_login(self.user1)

        response = self.client.get(reverse("my-health-info-last"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_equal_health_info(response.json(), new_health_info)

    def test_retrieve_my_health_info(self):
        """GET 요청으로 특정 건강 정보를 조회하는지 테스트"""
        self.client.force_login(self.user1)
        health_info = HealthInfo.objects.first()
        pk = health_info.pk

        response = self.client.get(reverse("my-health-info-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_equal_health_info(response.json(), self.user1_health_info)

    def test_post_my_health_info_with_invalid_age(self):
        """POST 요청으로 나이가 음수인 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        self.client.force_login(self.user1)

        new_health_info = {
            "age": -1,
            "height": 180,
            "weight": 70,
        }

        response = self.client.post(
            reverse("my-health-info-list"),
            data=new_health_info,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_my_health_info_with_not_allowed_method(self):
        """허용되지 않은 메소드로 my-health-info/에 접근할 때 405 에러를 리턴하는지 테스트"""
        self.client.force_login(self.user1)

        health_info = HealthInfo.objects.first()
        pk = health_info.pk

        new_health_info = self.create_fake_health_info_request()

        responses = {
            "put": self.client.put(
                reverse("my-health-info-detail", kwargs={"pk": pk}),
                data=new_health_info,
                content_type="application/json",
            ),
            "patch": self.client.patch(
                reverse("my-health-info-detail", kwargs={"pk": pk}),
                data=new_health_info,
                content_type="application/json",
            ),
            "delete": self.client.delete(
                reverse("my-health-info-detail", kwargs={"pk": pk})
            ),
        }

        for action, response in responses.items():
            with self.subTest(action=action):
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                    f"{action} did not return 405",
                )
