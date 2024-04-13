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

        self.user = FakeUser()
        self.user.create_instance()

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(user_instance=self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(user_instance=self.admin.instance)

    # 모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인
    def test_all_users_can_view_exercises_list(self):
        response = self.client.get(reverse("exercises-info-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.exercise1.instance.title)
        self.assertContains(response, self.exercise2.instance.title)

    # 모든 사용자가 운동 정보 상세를 볼 수 있는지 확인
    def test_all_users_can_view_exercise_detail(self):
        response = self.client.get(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.instance.title)

    # 관리자만 운동 정보를 생성할 수 있는지 확인
    def test_admin_can_create_exercise(self):
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        print(new_exercise.request_create())

        response = self.client.post(
            reverse("exercises-info-list"),
            data=new_exercise.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["title"], new_exercise.request_create()["title"])

    # 일반유저가 운동 정보를 생성할 수 있는지 확인
    def test_user_can_create_exercise(self):
        new_exercise = FakeExercisesInfo()

        self.client.force_login(self.user.instance)

        response = self.client.post(
            reverse("exercises-info-list"),
            data=new_exercise.request_create(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 관리자만 운동 정보를 수정할 수 있는지 확인
    def test_admin_can_update_exercise(self):
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data=new_exercise.request_create(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ExercisesInfo.objects.get(id=self.exercise1.instance.id).title,
            new_exercise.request_create()["title"],
        )

    # 일반유저가 운동 정보를 수정할 수 있는지 확인
    def test_user_can_update_exercise(self):
        new_exercise = FakeExercisesInfo()

        self.client.force_login(self.user.instance)

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data=new_exercise.request_create(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 관리자만 운동 정보를 삭제할 수 있는지 확인
    def test_admin_can_delete_exercise(self):
        self.client.force_login(self.admin.instance)

        response = self.client.delete(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # 일반유저가 운동 정보를 삭제할 수 있는지 확인
    def test_user_can_delete_exercise(self):
        self.client.force_login(self.user.instance)
        response = self.client.delete(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ExercisesInfo.objects.count(), 2)

    # 운동 정보 생성 시 필수 필드가 누락되었을 때 에러가 발생하는지 확인
    def test_exercise_create_error_when_required_field_is_missing(self):
        self.client.force_login(self.admin.instance)
        response = self.client.post(
            reverse("exercises-info-list"),
            data={},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
