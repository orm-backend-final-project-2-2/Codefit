from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="이메일")
    nickname = models.CharField(max_length=30, unique=True, verbose_name="닉네임")

    # 추가 요구사항: 프로필 사진을 위한 필드
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True, verbose_name="프로필 사진"
    )

    # 추가 요구사항: 사용자의 나이를 저장하는 필드
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="나이")

    # 추가 요구사항: 사용자의 소개를 저장하는 필드
    # bio = models.TextField(max_length=300, blank=True, verbose_name='소개')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    def __str__(self):
        return self.email
