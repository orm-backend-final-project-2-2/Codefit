import json
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo
from utils.fake_data import FakeUser, FakeExercisesInfo


class ExercisesInfoTestCase(TestCase):
    """초기설정을 위한 함수"""

    def setUp(self):
        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)
        self.admin_info = {
            "username": self.admin.instance.username,
            "password": "password",
        }

        self.user = FakeUser()
        self.user.create_instance()
        self.user_info = {
            "username": self.user.instance.username,
            "password": "password",
        }

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(user_instance=self.user.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(user_instance=self.user.instance)

    # 모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인
    def test_all_users_can_view_exercises_list(self):
        response = self.client.get(reverse("exercisesinfo-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.exercise1.instance.title)
        self.assertContains(response, self.exercise2.instance.title)

    # 모든 사용자가 운동 정보 상세를 볼 수 있는지 확인
    def test_all_users_can_view_exercise_detail(self):
        response = self.client.get(
            reverse("exercisesinfo-detail", kwargs={"pk": self.exercise1.instance.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.instance.title)

    # 관리자만 운동 정보를 생성할 수 있는지 확인
    def test_admin_can_create_exercise(self):
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        response = self.client.post(
            reverse("exercisesinfo-list"),
            data=new_exercise.request_create(),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["title"], new_exercise.request_create()["title"])

    # 일반유저가 운동 정보를 생성할 수 있는지 확인
    def test_user_can_create_exercise(self):
        new_exercise = FakeExercisesInfo()

        self.client.force_login(self.user.instance)

        response = self.client.post(
            reverse("exercisesinfo-list"),
            data=new_exercise.request_create(),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 관리자만 운동 정보를 수정할 수 있는지 확인
    def test_admin_can_update_exercise(self):
        self.client.login(**self.admin_info)

        # 데이터 전송 시 Content-Type 설정
        content_type = "application/json"
        data = json.dumps(self.exercise2_request)

        response = self.client.put(
            reverse("exercisesinfo-detail", args=[self.exercise1.id]),
            data=data,
            content_type=content_type,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ExercisesInfo.objects.get(id=self.exercise1.id).title,
            self.exercise2.title,
        )

    # 일반유저가 운동 정보를 수정할 수 있는지 확인
    def test_user_can_update_exercise(self):
        self.client.login(**self.user_info)
        response = self.client.put(
            reverse("exercisesinfo-detail", args=[self.exercise1.id]),
            data=self.exercise2_request,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            ExercisesInfo.objects.get(id=self.exercise1.id).title,
            self.exercise1.title,
        )

    # 관리자만 운동 정보를 삭제할 수 있는지 확인
    def test_admin_can_delete_exercise(self):
        self.client.login(**self.admin_info)
        response = self.client.delete(
            reverse("exercisesinfo-detail", args=[self.exercise1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExercisesInfo.objects.count(), 1)

    # 일반유저가 운동 정보를 삭제할 수 있는지 확인
    def test_user_can_delete_exercise(self):
        self.client.login(**self.user_info)
        response = self.client.delete(
            reverse("exercisesinfo-detail", args=[self.exercise1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ExercisesInfo.objects.count(), 2)

    # 운동 정보 생성 시 필수 필드가 누락되었을 때 에러가 발생하는지 확인
    def test_exercise_create_error_when_required_field_is_missing(self):
        self.client.login(**self.admin_info)
        response = self.client.post(
            reverse("exercisesinfo-list"),
            data={},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
