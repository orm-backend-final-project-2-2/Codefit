from django.test import TestCase
from account.models import CustomUser as User
from django.urls import reverse
from my_health_info.models import HealthInfo, Routine
from freezegun import freeze_time
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from utils.fake_data import FakeUser, FakeHealthInfo, FakeRoutine


class MyHealthInfoTestCase(TestCase):
    @freeze_time("2020-01-01")
    def setUp(self):
        """초기설정"""
        self.user1 = FakeUser()
        self.user1.create_instance()

        self.user1_health_info = FakeHealthInfo()
        self.user1_health_info.create_instance(user_instance=self.user1.instance)

    def calculate_users_bmi(self, health_info):
        """BMI 계산"""
        return health_info.get("weight") / ((health_info.get("height") / 100) ** 2)

    def assert_equal_health_info(self, health_info, expected_health_info):
        """건강 정보 비교"""

        expected_health_info = expected_health_info.request_create()

        self.assertEqual(health_info.get("age"), expected_health_info.get("age"))
        self.assertEqual(health_info.get("height"), expected_health_info.get("height"))
        self.assertEqual(health_info.get("weight"), expected_health_info.get("weight"))
        self.assertEqual(
            health_info.get("bmi"),
            self.calculate_users_bmi(expected_health_info),
        )

    def test_get_my_health_info_not_authenticated(self):
        """비로그인 유저가 my-helath-info/에 접근할 때 403 에러를 리턴하는지 테스트"""
        new_health_info = FakeHealthInfo()
        new_health_info_request = new_health_info.request_create()

        responses = {
            "list": self.client.get(reverse("my-health-info-list")),
            "create": self.client.post(
                reverse("my-health-info-list"),
                data=new_health_info_request,
                content_type="application/json",
            ),
            "retrieve": self.client.get(
                reverse("my-health-info-detail", kwargs={"pk": 1})
            ),
            "put": self.client.put(
                reverse("my-health-info-detail", kwargs={"pk": 1}),
                data=new_health_info_request,
                content_type="application/json",
            ),
            "patch": self.client.patch(
                reverse("my-health-info-detail", kwargs={"pk": 1}),
                data=new_health_info_request,
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
        new_user = FakeUser()
        new_user.create_instance()

        now = timezone.now()
        for days_back in range(40, -1, -1):
            past_day = now - timedelta(days=days_back)
            with freeze_time(f"{past_day.strftime('%Y-%m-%d')}"):
                new_health_info = FakeHealthInfo()
                new_health_info.create_instance(user_instance=new_user.instance)

        self.client.force_login(new_user.instance)

        response = self.client.get(reverse("my-health-info-list"))
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(data), 35)

    def test_post_my_health_info(self):
        """POST 요청으로 건강 정보를 생성하는지 테스트"""
        self.client.force_login(self.user1.instance)

        new_health_info = FakeHealthInfo()

        response = self.client.post(
            reverse("my-health-info-list"),
            data=new_health_info.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assert_equal_health_info(data, new_health_info)

    @freeze_time("2025-01-01")
    def test_reject_post_my_health_info_if_same_day(self):
        """POST 요청으로 같은 날짜에 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        new_health_info = FakeHealthInfo()

        self.client.force_login(self.user1.instance)

        response_1 = self.client.post(
            reverse("my-health-info-list"),
            data=new_health_info.request_create(),
            content_type="application/json",
        )
        response_2 = self.client.post(
            reverse("my-health-info-list"),
            data=new_health_info.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_my_health_info_last(self):
        """GET 요청으로 가장 최근 생성된 건강 정보를 조회하는지 테스트"""
        new_health_info = FakeHealthInfo()
        new_health_info.create_instance(user_instance=self.user1.instance)

        self.client.force_login(self.user1.instance)

        response = self.client.get(reverse("my-health-info-last"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_equal_health_info(response.json(), new_health_info)

    def test_retrieve_my_health_info(self):
        """GET 요청으로 특정 건강 정보를 조회하는지 테스트"""
        self.client.force_login(self.user1.instance)

        new_health_info = FakeHealthInfo()
        new_health_info.create_instance(user_instance=self.user1.instance)

        pk = new_health_info.instance.pk

        response = self.client.get(reverse("my-health-info-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_equal_health_info(response.json(), new_health_info)

    def test_post_my_health_info_with_invalid_age(self):
        """POST 요청으로 나이가 음수인 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        self.client.force_login(self.user1.instance)
        new_health_info = FakeHealthInfo()

        data = new_health_info.request_create()

        data.update({"age": -1})

        response = self.client.post(
            reverse("my-health-info-list"),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_my_health_info_with_not_allowed_method(self):
        """허용되지 않은 메소드로 my-health-info/에 접근할 때 405 에러를 리턴하는지 테스트"""
        self.client.force_login(self.user1.instance)

        health_info_first = HealthInfo.objects.first()
        pk = health_info_first.pk

        new_health_info = FakeHealthInfo()

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


class RoutineTestCase(TestCase):
    """
    목적: Routine 모델과 /routine/ API에 대한 테스트를 진행합니다.

    Test cases:
    1. 비로그인 유저가 /routine/에 접근할 때 403 에러를 리턴하는지 테스트
    2. 로그인한 유저가 /routine/에 접근할 때 유저의 루틴 정보를 조회하는지 테스트
    3. 루틴 생성 요청이 올바르게 처리되는지 테스트
    4. 비로그인 유저가 루틴 생성 요청을 보낼 때 403 에러를 리턴하는지 테스트
    5. 루틴 업데이트 요청이 올바르게 처리되는지 테스트
    6. 본인이 생성한 루틴이 아닌 경우 루틴 업데이트 요청이 403 에러를 리턴하는지 테스트
    7. 비로그인 유저가 루틴 업데이트 요청을 보낼 때 403 에러를 리턴하는지 테스트
    8. 루틴 삭제 요청이 올바르게 처리되는지 테스트
    9. 본인이 생성한 루틴이 아닌 경우 루틴 삭제 요청이 403 에러를 리턴하는지 테스트
    10. 비로그인 유저가 루틴 삭제 요청을 보낼 때 403 에러를 리턴하는지 테스트
    11. 허용되지 않은 메소드로 /routine/에 접근할 때 405 에러를 리턴하는지 테스트
    12. 루틴에 좋아요를 누르는 요청이 올바르게 처리되는지 테스트
    13. 루틴을 좋아요 순으로 정렬하여 조회할 수 있는지 테스트
    14. 이미 좋아요를 누른 루틴에 좋아요를 누르는 요청이 올바르게 처리되는지 테스트
    15. 루틴 목록에서 제작자로 검색하여 조회할 수 있는지 테스트
    16. 루틴 목록에서 자극 부위로 검색하여 조회할 수 있는지 테스트
    """

    def setUp(self):
        self.user1 = FakeUser()
        self.user1.create_instance()

        self.user2 = FakeUser()
        self.user2.create_instance()

        self.routine1 = FakeRoutine()
        self.routine1.create_instance(user_instance=self.user1.instance)

        self.routine2 = FakeRoutine()
        self.routine2.create_instance(user_instance=self.user2.instance)

        self.routine3 = FakeRoutine()
        self.routine3.create_instance(user_instance=self.user1.instance)

    def test_get_routine_not_authenticated(self):
        """
        비로그인 유저가 /routine/에 접근할 때 403 에러를 리턴하는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 비로그인 유저가 /routine/에 GET 요청을 보냅니다.
        2. 403 에러를 리턴하는지 확인합니다.
        """
        response = self.client.get(reverse("routine-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_routine_authenticated(self):
        """
        로그인한 유저가 /routine/에 접근할 때 루틴들을 조회하는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 로그인한 유저가 /routine/에 GET 요청을 보냅니다.
        2. 현재 생성된 루틴들을 조회하는지 확인합니다.
        """
        routines_count = Routine.objects.count()

        self.client.force_login(self.user1.instance)

        response = self.client.get(reverse("routine-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), routines_count)

    def test_post_routine(self):
        """
        루틴 생성 요청이 올바르게 처리되는지 테스트

        reverse_url: routine-list
        HTTP method: POST

        테스트 시나리오:
        1. 로그인한 유저가 /routine/에 POST 요청을 보냅니다.
        2. 루틴이 생성되었는지 확인합니다.
        """
        self.client.force_login(self.user1.instance)

        new_routine = FakeRoutine()

        response = self.client.post(
            reverse("routine-list"),
            data=new_routine.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data.get("username"), self.user1.instance.username)

    def test_post_routine_not_authenticated(self):
        """
        비로그인 유저가 루틴 생성 요청을 보낼 때 403 에러를 리턴하는지 테스트

        reverse_url: routine-list
        HTTP method: POST

        테스트 시나리오:
        1. 비로그인 유저가 /routine/에 POST 요청을 보냅니다.
        2. 403 에러를 리턴하는지 확인합니다.
        """
        new_routine = FakeRoutine()

        response = self.client.post(
            reverse("routine-list"),
            data=new_routine.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_routine(self):
        """
        루틴 업데이트 요청이 올바르게 처리되는지 테스트

        reverse_url: routine-detail
        HTTP method: PATCH

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/에 PATCH 요청을 보냅니다.
        2. 루틴이 업데이트되었는지 확인합니다.
        """
        self.client.force_login(self.user1.instance)

        pk = self.routine1.instance.pk

        new_routine = FakeRoutine()
        new_routine_title = "Updated Title"

        response = self.client.patch(
            reverse("routine-detail", kwargs={"pk": pk}),
            data={"title": new_routine_title},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data.get("title"), new_routine_title)

    def test_update_routine_not_authenticated(self):
        """
        비로그인 유저가 루틴 업데이트 요청을 보낼 때 403 에러를 리턴하는지 테스트

        reverse_url: routine-detail
        HTTP method: PATCH

        테스트 시나리오:
        1. 비로그인 유저가 /routine/<pk>/에 PATCH 요청을 보냅니다.
        2. 403 에러를 리턴하는지 확인합니다.
        """
        pk = self.routine1.instance.pk

        new_routine = FakeRoutine()
        new_routine_title = "Updated Title"

        response = self.client.patch(
            reverse("routine-detail", kwargs={"pk": pk}),
            data={"title": new_routine_title},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_routine_not_author(self):
        """
        본인이 생성한 루틴이 아닌 경우 루틴 업데이트 요청이 403 에러를 리턴하는지 테스트

        reverse_url: routine-detail
        HTTP method: PATCH

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/에 PATCH 요청을 보냅니다.
        2. 403 에러를 리턴하는지 확인합니다.
        """
        self.client.force_login(self.user2.instance)

        pk = self.routine1.instance.pk

        new_routine = FakeRoutine()
        new_routine_title = "Updated Title"

        response = self.client.patch(
            reverse("routine-detail", kwargs={"pk": pk}),
            data={"title": new_routine_title},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_routine(self):
        """
        루틴 삭제 요청이 올바르게 처리되는지 테스트

        reverse_url: routine-detail
        HTTP method: DELETE

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/에 DELETE 요청을 보냅니다.
        2. 루틴이 삭제되었는지 확인합니다.
        """
        self.client.force_login(self.user1.instance)

        pk = self.routine1.instance.pk

        response = self.client.delete(reverse("routine-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Routine.objects.filter(pk=pk).exists())

    def test_delete_routine_not_authenticated(self):
        """
        비로그인 유저가 루틴 삭제 요청을 보낼 때 403 에러를 리턴하는지 테스트

        reverse_url: routine-detail
        HTTP method: DELETE

        테스트 시나리오:
        1. 비로그인 유저가 /routine/<pk>/에 DELETE 요청을 보냅니다.
        2. 403 에러를 리턴하는지 확인합니다.
        """
        pk = self.routine1.instance.pk

        response = self.client.delete(reverse("routine-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_routine_not_author(self):
        """
        본인이 생성한 루틴이 아닌 경우 루틴 삭제 요청이 403 에러를 리턴하는지 테스트

        reverse_url: routine-detail
        HTTP method: DELETE

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/에 DELETE 요청을 보냅니다.
        2. 403 에러를 리턴하는지 확인합니다.
        """
        self.client.force_login(self.user2.instance)

        pk = self.routine1.instance.pk

        response = self.client.delete(reverse("routine-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_routine_not_allowed_method(self):
        """
        허용되지 않은 메소드로 /routine/에 접근할 때 405 에러를 리턴하는지 테스트

        reverse_url: routine-detail
        HTTP method: PUT

        테스트 시나리오:
        1. 로그인한 유저가 /routine/에 PUT 요청을 보냅니다.
        2. 405 에러를 리턴하는지 확인합니다.
        """
        self.client.force_login(self.user1.instance)

        pk = self.routine1.instance.pk

        response = self.client.put(reverse("routine-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_like_routine(self):
        """
        루틴에 좋아요를 누르는 요청이 올바르게 처리되는지 테스트

        reverse_url: routine-like
        HTTP method: POST

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/like/에 POST 요청을 보냅니다.
        2. 루틴에 좋아요가 추가되었는지 확인합니다.
        """
        self.client.force_login(self.user1.instance)

        like_count = self.routine2.instance.like_count

        pk = self.routine2.instance.pk

        response = self.client.post(reverse("routine-like", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertTrue(data.get("like_count"), like_count + 1)

    def test_like_routine_already_liked(self):
        """
        이미 좋아요를 누른 루틴에 좋아요를 누르는 요청이 올바르게 처리되는지 테스트

        reverse_url: routine-like
        HTTP method: POST

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/like/에 POST 요청을 두 번 보냅니다.
        2. 405 에러를 리턴하는지 확인합니다.
        """
        self.client.force_login(self.user1.instance)

        pk = self.routine2.instance.pk

        self.client.post(reverse("routine-like", kwargs={"pk": pk}))

        response = self.client.post(reverse("routine-like", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_routine_sorted_by_like(self):
        """
        루틴을 좋아요 순으로 정렬하여 조회할 수 있는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 새로운 유저 몇 명을 생성합니다.
        2. 새로운 루틴 몇 개를 생성합니다.
        3. 기존 루틴과 새로운 루틴에 좋아요 수를 변경합니다.
        4. 루틴을 좋아요 순으로 정렬합니다.
        5. /routine/에 GET 요청을 보냅니다.
        6. Response의 루틴들이 정렬해둔 루틴의 좋아요와 일치하는지 확인합니다.
        """
        new_user_1 = FakeUser()
        new_user_1.create_instance()

        new_user_2 = FakeUser()
        new_user_2.create_instance()

        new_user_3 = FakeUser()
        new_user_3.create_instance()

        new_routine_1 = FakeRoutine()
        new_routine_1.create_instance(user_instance=new_user_1.instance)

        new_routine_2 = FakeRoutine()
        new_routine_2.create_instance(user_instance=new_user_2.instance)

        new_routine_1.instance.like_count = 10
        new_routine_1.instance.save()

        new_routine_2.instance.like_count = 5
        new_routine_2.instance.save()

        sorted_routines = Routine.objects.all().order_by("-like_count")

        self.client.force_login(self.user1.instance)

        response = self.client.get(reverse("routine-list") + "?ordering=-like_count")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        for routine_instances, response_routine in zip(sorted_routines, data):
            self.assertEqual(
                routine_instances.like_count, response_routine.get("like_count")
            )

    def test_search_routine_by_author(self):
        """
        루틴 목록에서 제작자로 검색하여 조회할 수 있는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 로그인한 유저가 /routine/에 GET 요청을 보냅니다.
        2. Response의 루틴들이 로그인한 유저가 생성한 루틴들만 조회되는지 확인합니다.
        """

        self.client.force_login(self.user1.instance)

        response = self.client.get(
            reverse("routine-list") + f"?author__id={self.user1.instance.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        for routine in data:
            self.assertEqual(routine.get("username"), self.user1.instance.username)
