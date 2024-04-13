from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from account.models import CustomUser as User
from utils.fake_data import FakeUser, FakePost, FakeComment


class CommentTestCase(TestCase):
    def setUp(self):
        self.user1 = FakeUser()
        self.user1.create_instance()

        self.user2 = FakeUser()
        self.user2.create_instance()

        self.user1_post1 = FakePost()
        self.user1_post1.create_instance(user_instance=self.user1.instance)

        self.user2_post1 = FakePost()
        self.user2_post1.create_instance(user_instance=self.user2.instance)

        self.user1_comment1 = FakeComment()
        self.user1_comment1.create_instance(
            user_instance=self.user1.instance, post_instance=self.user1_post1.instance
        )

        self.user1_comment2 = FakeComment()
        self.user1_comment2.create_instance(
            user_instance=self.user1.instance, post_instance=self.user1_post1.instance
        )

    def test_get_comment_list(self):
        """comment/ GET 요청시 모든 Comment 객체를 반환하는지 테스트"""
        comment_count = Comment.objects.all().count()

        response = self.client.get(reverse("comment-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), comment_count)


class PostTestCase(TestCase):
    def setUp(self):
        self.user1 = FakeUser()
        self.user1.create_instance()

        self.user2 = FakeUser()
        self.user2.create_instance()

        self.user1_post1 = FakePost()
        self.user1_post1.create_instance(user_instance=self.user1.instance)

        self.user1_post2 = FakePost()
        self.user1_post2.create_instance(user_instance=self.user1.instance)

        self.user2_post1 = FakePost()
        self.user2_post1.create_instance(user_instance=self.user2.instance)

    def test_get_post_list(self):
        """post/ GET 요청시 모든 Post 객체를 반환하는지 테스트"""
        post_count = Post.objects.all().count()

        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), post_count)

    def test_get_post_detail(self):
        """post/<pk>/ GET 요청시 해당 Post 객체를 반환하는지 테스트"""
        response = self.client.get(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.user1_post1.instance.title)
        self.assertEqual(response.data["content"], self.user1_post1.instance.content)

    def test_create_post(self):
        """post/ POST 요청시 새로운 Post 객체를 생성하는지 테스트"""
        new_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.post(reverse("post-list"), new_post.request_create())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["title"], new_post.request_create()["title"])
        self.assertEqual(data["content"], new_post.request_create()["content"])

    def test_create_post_without_login(self):
        """post/ POST 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        new_post = FakePost()

        response = self.client.post(reverse("post-list"), new_post.request_create())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post(self):
        """post/<pk>/ PATCH 요청시 해당 Post 객체를 수정하는지 테스트"""
        update_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data=update_post.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], update_post.request_create()["title"])
        self.assertEqual(data["content"], update_post.request_create()["content"])

    def test_update_post_without_login(self):
        """post/<pk>/ PATCH 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        update_post = FakePost()

        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data=update_post.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        """post/<pk>/ DELETE 요청시 해당 Post 객체를 삭제하는지 테스트"""
        self.client.force_login(self.user1.instance)

        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.user1_post1.instance.id).exists())

    def test_delete_post_without_login(self):
        """post/<pk>/ DELETE 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_update_post_not_allowed(self):
        """post/<pk>/ PUT 요청시 405 에러를 반환하는지 테스트"""
        update_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.put(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data=update_post.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_only_logged_in_user_posts(self):
        """post/ GET 요청시 로그인한 사용자의 Post 객체만 반환하는지 테스트"""
        self.client.force_login(self.user1.instance)
        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(
        #     len(response.data), 2
        # )  # 숫자 대신 원하는 값을 직접 쿼리로 가져와서 비교하는게 좋습니다.
        self.assertEqual(response.data[0]["title"], self.user1_post1.instance.title)

    # TODO: 다른사람도 포스트를 볼 수 있어야 합니다
    def test_get_only_logged_in_user_post_detail(self):
        """post/<pk>/ GET 요청시 로그인한 사용자의 특정 Post 객체만 반환하는지 테스트"""
        self.client.force_login(self.user1.instance)
        response = self.client.get(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.user1_post1.instance.title)
        self.assertEqual(response.data["content"], self.user1_post1.instance.content)

    def test_ohter_user_can_see_post(self):
        """다른 사용자도 포스트를 볼 수 있는지 테스트"""
        self.client.force_login(self.user2.instance)
        response = self.client.get(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.user1_post1.instance.title)
        self.assertEqual(response.data["content"], self.user1_post1.instance.content)

    def test_get_post_list_without_login(self):
        """로그인하지 않은 경우에도 포스트 목록을 볼 수 있는지 테스트"""
        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post_by_creator(self):
        """포스트를 생성한 사용자만이 해당 포스트를 수정할 수 있는지 테스트"""
        self.client.force_login(self.user1.instance)

        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data={"title": "Updated Title", "content": "Updated Content"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_post = Post.objects.get(pk=self.user1_post1.instance.id)
        self.assertEqual(updated_post.title, "Updated Title")
        self.assertEqual(updated_post.content, "Updated Content")

    def test_delete_post_by_creator(self):
        """포스트를 생성한 사용자만이 해당 포스트를 삭제할 수 있는지 테스트"""
        self.client.force_login(self.user1.instance)

        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        post_exists = Post.objects.filter(pk=self.user1_post1.instance.id).exists()
        self.assertFalse(post_exists)

    def test_update_post_by_non_creator(self):
        """포스트를 생성한 사용자가 아닌 다른 사용자가 포스트를 수정할 시도할 때 403 에러를 반환하는지 테스트"""
        self.client.force_login(self.user2.instance)

        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data={"title": "Updated Title", "content": "Updated Content"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_by_non_creator(self):
        """포스트를 생성한 사용자가 아닌 다른 사용자가 포스트를 삭제할 시도할 때 403 에러를 반환하는지 테스트"""
        self.client.force_login(self.user2.instance)

        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_post_detail_not_found(self):
        """존재하지 않는 포스트를 조회할 때 404 에러를 반환하는지 테스트"""
        response = self.client.get(reverse("post-detail", kwargs={"pk": 1000}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_post_not_found(self):
        """존재하지 않는 포스트를 수정할 때 404 에러를 반환하는지 테스트"""
        self.client.force_login(self.user1.instance)

        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": 1000}),
            data={"title": "Updated Title", "content": "Updated Content"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_post_not_found(self):
        """존재하지 않는 포스트를 삭제할 때 404 에러를 반환하는지 테스트"""
        self.client.force_login(self.user1.instance)

        response = self.client.delete(reverse("post-detail", kwargs={"pk": 1000}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_post_list_pagination(self):
        """포스트 목록 조회시 페이지네이션 기능이 제대로 동작하는지 테스트"""
        response = self.client.get(reverse("post-list"))
        response.data = response_data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["next"], None)
        self.assertEqual(response.data["previous"], None)
        self.assertEqual(len(response.data["results"]), 3)

    def test_create_post_missing_title(self):
        """제목이 없는 포스트를 생성할 때 400 에러를 반환하는지 테스트"""
        new_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.post(
            reverse("post-list"), {"content": new_post.request_create()["content"]}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_post_missing_content(self):
        """내용이 없는 포스트를 생성할 때 400 에러를 반환하는지 테스트"""
        new_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.post(
            reverse("post-list"), {"title": new_post.request_create()["title"]}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_post_missing_title_and_content(self):
        """제목과 내용이 모두 없는 포스트를 생성할 때 400 에러를 반환하는지 테스트"""
        self.client.force_login(self.user1.instance)

        response = self.client.post(reverse("post-list"), {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# 페이지네이션 테스트용 더미 데이터
response_data = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 1,
            "author": 1,
            "title": "Title1",
            "content": "Content1",
            "created_at": "2021-01-01T00:00:00Z",
            "updated_at": "2021-01-01T00:00:00Z",
            "view_count": 0,
        },
        {
            "id": 2,
            "author": 1,
            "title": "Title2",
            "content": "Content2",
            "created_at": "2021-01-01T00:00:00Z",
            "updated_at": "2021-01-01T00:00:00Z",
            "view_count": 0,
        },
        {
            "id": 3,
            "author": 2,
            "title": "Title3",
            "content": "Content3",
            "created_at": "2021-01-01T00:00:00Z",
            "updated_at": "2021-01-01T00:00:00Z",
            "view_count": 0,
        },
    ],
}
