from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Post
from .serializers import PostSerializer
from django.contrib.auth.models import User


class PostTestCase(TestCase):
    def setUp(self):
        self.user1_info = {"username": "user1", "password": "password1"}
        self.user1 = User.objects.create_user(**self.user1_info)
        self.user1_post1_info = {
            "title": "title1",
            "content": "content1",
        }
        self.user1_post1 = Post.objects.create(
            author=self.user1, **self.user1_post1_info
        )
        self.user1_post2_info = {
            "title": "title2",
            "content": "content2",
        }
        self.user1_post2 = Post.objects.create(
            author=self.user1, **self.user1_post2_info
        )

    def test_get_post_list(self):
        """post/ GET 요청시 모든 Post 객체를 반환하는지 테스트"""
        post_count = Post.objects.all().count()

        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), post_count)

    def test_get_post_detail(self):
        """post/<pk>/ GET 요청시 해당 Post 객체를 반환하는지 테스트"""
        response = self.client.get(reverse("post-detail", args=[self.user1_post1.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.user1_post1.title)
        self.assertEqual(response.data["content"], self.user1_post1.content)

    def test_create_post(self):
        """post/ POST 요청시 새로운 Post 객체를 생성하는지 테스트"""
        new_post_info = {
            "title": "new title",
            "content": "new content",
        }
        self.client.force_login(self.user1)
        response = self.client.post(reverse("post-list"), new_post_info)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["title"], new_post_info["title"])
        self.assertEqual(data["content"], new_post_info["content"])

    def test_create_post_without_login(self):
        """post/ POST 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        new_post_info = {
            "title": "new title",
            "content": "new content",
        }
        response = self.client.post(reverse("post-list"), new_post_info)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post(self):
        """post/<pk>/ PUT 요청시 해당 Post 객체를 수정하는지 테스트"""
        update_post_info = {
            "title": "update title",
        }
        self.client.force_login(self.user1)
        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.id}),
            data=update_post_info,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], update_post_info["title"])

    def test_update_post_without_login(self):
        """post/<pk>/ PUT 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        update_post_info = {
            "title": "update title",
        }
        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.id}),
            data=update_post_info,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        """post/<pk>/ DELETE 요청시 해당 Post 객체를 삭제하는지 테스트"""
        self.client.force_login(self.user1)
        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.user1_post1.id).exists())

    def test_delete_post_without_login(self):
        """post/<pk>/ DELETE 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
