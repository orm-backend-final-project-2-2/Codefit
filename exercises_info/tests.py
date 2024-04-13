from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo
from utils.fake_data import FakeExercisesInfo, FakeUser


class ExercisesInfoTestCase(TestCase):
    """
    목적: ExercisesInfo App의 API 테스트

    Test cases:
    1. 모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인
    2. 모든 사용자가 운동 정보 상세 페이지를 볼 수 있는지 확인
    3. 관리자만 운동 정보를 생성할 수 있는지 확인
    4. 일반유저가 운동 정보를 생성할 수 있는지 확인
    5. 관리자만 운동 정보를 수정할 수 있는지 확인
    6. 일반유저가 운동 정보를 수정할 수 있는지 확인
    7. 관리자만 운동 정보를 삭제할 수 있는지 확인
    8. 일반유저가 운동 정보를 삭제할 수 있는지 확인
    9. 운동 정보 생성 시 필수 필드가 누락되었을 때 에러가 발생하는지 확인
    10. Enum에 존재하지 않는 Focus Area를 입력했을 때 에러가 발생하는지 확인
    11. Focus Area의 수정 요청이 올바르게 처리되는지 확인
    12. Title의 길이가 100자를 초과했을 때 에러가 발생하는지 확인
    13. Description의 길이가 1000자를 초과했을 때 에러가 발생하는지 확인
    """

    def setUp(self):
        """
        사전 설정

        1. 관리자 계정 생성
        2. 일반 사용자 계정 생성
        3. 관리자 계정으로 운동 정보 2개 생성
        """
        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.user = FakeUser()
        self.user.create_instance()

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(user_instance=self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(user_instance=self.admin.instance)

    def test_all_users_can_view_exercises_list(self):
        """
        모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인

        reverse_url : exercises-info-list
        HTTP method : GET

        테스트 시나리오:
        1. 서버에 GET 요청을 보냄
        3. 응답 코드가 200인지 확인
        4. 응답 데이터의 길이가 저장된 운동 정보 리스트의 요소 개수와 같은지 확인
        """
        exercise_count = ExercisesInfo.objects.count()

        response = self.client.get(reverse("exercises-info-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), exercise_count)

    def test_all_users_can_retrieve_exercise_detail(self):
        """
        모든 사용자가 운동 정보 상세 페이지를 볼 수 있는지 확인

        reverse_url : exercises-info-detail
        HTTP method : GET

        테스트 시나리오:
        1. 서버에 첫 번째로 생성한 운동 정보의 id로 GET 요청을 보냄
        2. 응답 코드가 200인지 확인
        3. 응답 데이터에 id에 해당하는 운동 정보의 제목이 있는지 확인
        """

        response = self.client.get(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.instance.title)

    def test_admin_can_create_exercise(self):
        """
        관리자만 운동 정보를 생성할 수 있는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 새로운 운동 정보 생성
        3. 응답 코드가 201인지 확인
        4. 응답 데이터에 생성한 운동 정보의 제목이 있는지 확인
        """
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        response = self.client.post(
            reverse("exercises-info-list"),
            data=new_exercise.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["title"], new_exercise.request_create()["title"])

    def test_user_can_create_exercise(self):
        """
        일반유저가 운동 정보를 생성하려고 시도할 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 일반 유저 계정으로 로그인
        2. 서버에 POST 요청을 보내서 새로운 운동 정보 생성
        3. 응답 코드가 403인지 확인
        """
        new_exercise = FakeExercisesInfo()

        self.client.force_login(self.user.instance)

        response = self.client.post(
            reverse("exercises-info-list"),
            data=new_exercise.request_create(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_exercise(self):
        """
        관리자만 운동 정보를 수정할 수 있는지 확인

        reverse_url : exercises-info-detail
        HTTP method : PATCH

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 PATCH 요청을 보내서 운동 정보 수정
        4. 응답 코드가 200인지 확인
        """
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

    def test_user_can_update_exercise(self):
        """
        일반유저가 운동 정보를 수정하려고 시도할 때 에러가 발생하는지 확인

        reverse_url : exercises-info-detail
        HTTP method : PATCH

        테스트 시나리오:
        1. 일반 유저 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 PATCH 요청을 보내서 운동 정보 수정
        4. 응답 코드가 403인지 확인
        """
        new_exercise = FakeExercisesInfo()

        self.client.force_login(self.user.instance)

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data=new_exercise.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_exercise(self):
        """
        관리자만 운동 정보를 삭제할 수 있는지 확인

        reverse_url : exercises-info-detail
        HTTP method : DELETE

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 DELETE 요청을 보내서 운동 정보 삭제
        3. 응답 코드가 204인지 확인
        """
        self.client.force_login(self.admin.instance)

        response = self.client.delete(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_delete_exercise(self):
        """
        일반유저가 운동 정보를 삭제하려고 시도할 때 에러가 발생하는지 확인

        reverse_url : exercises-info-detail
        HTTP method : DELETE

        테스트 시나리오:
        1. 일반 유저 계정으로 로그인
        2. 서버에 DELETE 요청을 보내서 운동 정보 삭제
        3. 응답 코드가 403인지 확인
        """
        self.client.force_login(self.user.instance)
        response = self.client.delete(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ExercisesInfo.objects.count(), 2)

    def test_exercise_create_error_when_required_field_is_missing(self):
        """
        운동 정보 생성 시 필수 필드가 누락되었을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 필수 필드가 누락된 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.client.force_login(self.admin.instance)
        response = self.client.post(
            reverse("exercises-info-list"),
            data={},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exercise_create_error_when_focus_area_is_not_in_enum(self):
        """
        Enum에 존재하지 않는 Focus Area를 입력했을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 Enum에 존재하지 않는 Focus Area를 입력한 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()

        request_data["focus_areas"] = [
            {
                "focus_area": "test",
            }
        ]

        response = self.client.post(
            reverse("exercises-info-list"),
            data=request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_focus_areas_successsfully(self):
        """
        Focus Area의 수정 요청이 올바르게 처리되는지 확인

        reverse_url : exercises-info-detail
        HTTP method : PATCH

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 PATCH 요청을 보내서 Focus Area 수정
        4. 응답 코드가 200인지 확인
        """
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data={"focus_areas": new_exercise.request_create().get("focus_areas")},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        focus_areas = data.get("focus_areas")

        self.assertEqual(focus_areas, new_exercise.request_create().get("focus_areas"))

    def test_title_length_error(self):
        """
        Title의 길이가 100자를 초과했을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 Title의 길이가 100자를 초과한 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()
        request_data["title"] = "a" * 101

        response = self.client.post(
            reverse("exercises-info-list"),
            data=request_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_description_length_error(self):
        """
        Description의 길이가 1000자를 초과했을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 Description의 길이가 1000자를 초과한 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.client.force_login(self.admin.instance)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()
        request_data["description"] = "a" * 1001

        response = self.client.post(
            reverse("exercises-info-list"),
            data=request_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

