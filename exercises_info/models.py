from django.db import models
from account.models import CustomUser as User
from utils.enums import FocusAreaEnum


class ExercisesInfo(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exercises_info"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    video = models.FileField(upload_to="exercises_info_video/", blank=True)
    focus_areas = models.ManyToManyField(
        FocusAreaEnum, verbose_name="Focus Areas", related_name="exercise"
    )
    # exercise_attributes = models.OneToOneField(
    #     "ExercisesAttribute", on_delete=models.CASCADE, related_name="exercise"
    # )

    def __str__(self):
        return f"{self.title}"


# class ExercisesAttribute(models.Model):
#     need_set = models.BooleanField(default=False)
#     need_rep = models.BooleanField(default=False)
#     need_weight = models.BooleanField(default=False)
#     need_duration = models.BooleanField(default=False)
#     need_speed = models.BooleanField(default=False)
