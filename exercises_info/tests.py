from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from exercises_info.models import ExercisesInfo


class ExercisesInfoTestCase(TestCase):
    """초기설정을 위한 함수"""

    def setUp(self):
        # 관리자 계정 생성
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )

        # 일반 사용자 계정 생성
        self.user = User.objects.create_user(username="testuser", password="password")

        # 운동 정보 생성
        self.exercise1 = ExercisesInfo.objects.create(
            author=self.admin,
            title="Bench Press",
            description="A chest exercise",
        )
        self.exercise2 = ExercisesInfo.objects.create(
            author=self.user,
            title="Deadlift",
            description="A back exercise",
        )

    # 모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인
    def test_all_users_can_view_exercises_list(self):
        client = Client()
        response = client.get(reverse("exercisesinfo-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.title)
        self.assertContains(response, self.exercise2.title)

    # 모든 사용자가 운동 정보 상세를 볼 수 있는지 확인
    def test_all_users_can_view_exercise_detail(self):
        client = Client()
        response = client.get(reverse("exercisesinfo-detail", args=[self.exercise1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.title)

        response = client.get(reverse("exercisesinfo-detail", args=[self.exercise2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise2.title)

    # 관리자만 운동 정보를 생성할 수 있는지 확인
    def test_admin_can_create_exercise(self):
        client = Client()
        client.login(username="admin", password="password")
        response = client.post(
            reverse("exercisesinfo-list"),
            {
                "author": self.admin.id,
                "title": "Squat",
                "description": "A leg exercise",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ExercisesInfo.objects.count(), 3)

    # 일반유저가 운동 정보를 생성할 수 있는지 확인
    def test_user_can_create_exercise(self):
        client = Client()
        client.login(username="testuser", password="password")
        response = client.post(
            reverse("exercisesinfo-list"),
            {
                "author": self.user.id,
                "title": "Squat",
                "description": "A leg exercise",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ExercisesInfo.objects.count(), 2)
