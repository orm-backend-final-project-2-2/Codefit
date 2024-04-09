from django.test import Client, TestCase
from django.urls import reverse
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
        self.exercise1.create_instance(user_instance=self.user.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(user_instance=self.user.instance)

    # 모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인
    def test_all_users_can_view_exercises_list(self):
        response = self.client.get(reverse("exercisesinfo-list"))

        self.assertEqual(response.status_code, 200)
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

        self.assertEqual(response.status_code, 201)

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
        self.assertEqual(response.status_code, 403)
