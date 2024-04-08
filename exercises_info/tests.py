from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from faker import Faker
from exercises_info.models import ExercisesInfo


class ExercisesInfoTestCase(TestCase):
    """초기설정을 위한 함수"""

    def setUp(self):
        self.fake = Faker()
        self.admin_info = self.create_fake_user_info()

        self.admin = User.objects.create_superuser(**self.admin_info)
        self.user_info = self.create_fake_user_info()
        self.user = User.objects.create_user(**self.user_info)

        self.exercise1_request = self.create_fake_exercise_request()
        self.exercise1 = ExercisesInfo.objects.create(
            author=self.admin, **self.exercise1_request
        )
        self.exercise2_request = self.create_fake_exercise_request()
        self.exercise2 = ExercisesInfo.objects.create(
            author=self.admin, **self.exercise2_request
        )

    def create_fake_user_info(self):
        return {
            "username": self.fake.user_name(),
            "password": self.fake.password(),
        }

    def create_fake_exercise_request(self):
        return {
            "title": self.fake.word(),
            "description": self.fake.text(),
        }

    # 모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인
    def test_all_users_can_view_exercises_list(self):
        response = self.client.get(reverse("exercisesinfo-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.title)
        self.assertContains(response, self.exercise2.title)

    # 모든 사용자가 운동 정보 상세를 볼 수 있는지 확인
    def test_all_users_can_view_exercise_detail(self):
        response = self.client.get(
            reverse("exercisesinfo-detail", args=[self.exercise1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.title)

        response = self.client.get(
            reverse("exercisesinfo-detail", args=[self.exercise2.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise2.title)

    # 관리자만 운동 정보를 생성할 수 있는지 확인
    def test_admin_can_create_exercise(self):
        self.client.login(**self.admin_info)
        response = self.client.post(
            reverse("exercisesinfo-list"),
            data=self.exercise1_request,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ExercisesInfo.objects.count(), 3)

    # 일반유저가 운동 정보를 생성할 수 있는지 확인
    def test_user_can_create_exercise(self):
        self.client.login(**self.user_info)
        response = self.client.post(
            reverse("exercisesinfo-list"),
            data=self.exercise1_request,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ExercisesInfo.objects.count(), 2)
