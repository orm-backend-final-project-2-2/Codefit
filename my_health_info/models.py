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
        User, on_delete=models.SET_NULL, null=True, related_name="written_routines"
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


class MirroredRoutine(models.Model):
    title = models.CharField(max_length=50)
    author_name = models.CharField(max_length=50)
    original_routine = models.OneToOneField(
        Routine, related_name="mirrored_routine", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f"{self.author_name}의 루틴: {self.title}"


class ExerciseInRoutine(models.Model):
    routine = models.ForeignKey(
        Routine,
        related_name="exercises_in_routine",
        on_delete=models.SET_NULL,
        null=True,
    )
    mirrored_routine = models.ForeignKey(
        MirroredRoutine,
        related_name="exercises_in_routine",
        on_delete=models.SET_NULL,
        null=True,
    )
    exercise = models.ForeignKey(
        ExercisesInfo,
        related_name="exercises_in_routine",
        on_delete=models.SET_NULL,
        null=True,
    )
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = (("routine", "order"), ("mirrored_routine", "order"))

    def __str__(self):
        return f"{self.routine.title}의 {self.order}번째 운동: {self.exercise.title}"


class UsersRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    routine = models.ForeignKey(
        Routine,
        related_name="subscribers",
        on_delete=models.SET_NULL,
        null=True,
    )
    mirrored_routine = models.ForeignKey(
        MirroredRoutine,
        related_name="mirrored_subscribers",
        on_delete=models.SET_NULL,
        null=True,
    )
    need_update = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "routine"), ("user", "mirrored_routine"))

    def __str__(self):
        if self.routine:
            return f"{self.user.username}이 {self.routine.author.username}의 루틴을 구독중: {self.routine.title}"
        return f"{self.user.username}이 {self.mirrored_routine.author_name}의 루틴을 구독중: {self.mirrored_routine.title}"
