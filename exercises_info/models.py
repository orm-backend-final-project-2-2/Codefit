from django.db import models
from account.models import CustomUser as User
from utils.enums import FocusAreaEnum


class FocusArea(models.Model):
    focus_area = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.focus_area}"


class ExercisesInfo(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exercises_info"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    video = models.CharField(max_length=200)

    focus_areas = models.ManyToManyField(
        FocusArea, related_name="exercises_info", blank=True
    )

    def __str__(self):
        return f"{self.title}"


# class ExercisesAttribute(models.Model):
#     need_set = models.BooleanField(default=False)
#     need_rep = models.BooleanField(default=False)
#     need_weight = models.BooleanField(default=False)
#     need_duration = models.BooleanField(default=False)
#     need_speed = models.BooleanField(default=False)
