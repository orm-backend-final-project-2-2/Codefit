from django.db import models
from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo


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
    is_mirrored = models.BooleanField(default=False)
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


class ExerciseInRoutine(models.Model):
    routine = models.ForeignKey(
        Routine, related_name="exercises_in_routine", on_delete=models.CASCADE
    )
    exercise = models.ForeignKey(
        ExercisesInfo, related_name="exercises_in_routine", on_delete=models.CASCADE
    )
    is_mirrored = models.BooleanField(default=False)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ["routine", "order"]

    def __str__(self):
        return f"{self.routine.title}의 {self.order}번째 운동: {self.exercise.title}"


class UsersRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    routine = models.ForeignKey(
        Routine, related_name="subscribers", on_delete=models.SET_NULL, null=True
    )
    mirrored_routine = models.OneToOneField(
        Routine, related_name="owner", on_delete=models.CASCADE, null=True
    )
    need_update = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "routine"]

    def __str__(self):
        if self.user == self.routine.author:
            return f"{self.user.username}의 루틴: {self.routine.title}"
        if not User.objects.filter(id=self.routine.author.id).exists():
            return f"이미 탈퇴한 유저의 루틴: {self.routine.title}"

        return f"{self.user.username}이 {self.routine.author.username}의 루틴을 구독: {self.routine.title}"
