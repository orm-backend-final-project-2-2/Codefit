from django.db import models
from account.models import CustomUser as User


# Create your models here.
class HealthInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    bmi = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}의 건강 정보"

    def save(self, *args, **kwargs):
        self.bmi = float(self.weight) / ((float(self.height) / 100) ** 2)
        super().save(*args, **kwargs)


class Routine(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default="탈퇴한 유저"
    )
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.author.username}의 루틴 정보"


class Routine_Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "routine"]

    def __str__(self):
        return f"{self.user.username}이 {self.routine.title}을 좋아합니다."

    def save(self, *args, **kwargs):
        self.routine.like_count += 1
        self.routine.save()
        super().save(*args, **kwargs)
