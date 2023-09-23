from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import time
from annoying.fields import AutoOneToOneField


class User(AbstractUser):
    # TODO: figure out how to make a Schedule for a User by default
    is_advisor = models.BooleanField(default=False)
    advisor = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)


def display_name(user: User):
    return f"{user.first_name} {user.last_name} ({user.username})"


class Class(models.Model):
    class Meta:
        unique_together = ("semester", "class_number")

    name = models.CharField(max_length=400)
    class_number = models.IntegerField(default=0)
    semester = models.CharField(max_length=10, default="")
    source_data = models.JSONField(default=dict)
    subject = models.CharField(max_length=10, default="")
    catalog_number = models.CharField(max_length=10, default="0000")
    class_section = models.CharField(max_length=10, default="001")
    component = models.CharField(max_length=10, default="LEC")
    units = models.CharField(max_length=10, default="3")

    def __str__(self):
        return self.name

    def meeting_days(self):
        days = {}
        for meeting in self.source_data["meetings"]:
            for i in range(0, len(meeting["days"]), 2):
                days[meeting["days"][i : i + 2]] = (
                    meeting["start_time"],
                    meeting["end_time"],
                )
        return days


def classes_overlap(class1, class2):
    meeting_days_1 = class1.meeting_days()
    meeting_days_2 = class2.meeting_days()
    for day in set(meeting_days_1.keys()).intersection(set(meeting_days_2.keys())):
        start_1_t = tuple(int(i) for i in meeting_days_1[day][0].split(".")[:3])
        end_1_t = tuple(int(i) for i in meeting_days_1[day][1].split(".")[:3])
        start_2_t = tuple(int(i) for i in meeting_days_2[day][0].split(".")[:3])
        end_2_t = tuple(int(i) for i in meeting_days_2[day][1].split(".")[:3])
        start_1 = time(*start_1_t)
        end_1 = time(*end_1_t)
        start_2 = time(*start_2_t)
        end_2 = time(*end_2_t)
        if start_1 <= start_2 < end_1:
            return True
        elif start_2 <= start_1 < end_2:
            return True
    return False


class Schedule(models.Model):
    connected_user = AutoOneToOneField(User, on_delete=models.CASCADE)
    classes = models.ManyToManyField(Class)
    visible = models.BooleanField(default=False, null=False, blank=False)
    approved = models.BooleanField(default=None, null=True, blank=False)

    def class_can_be_added(self, new_class):
        schedule = self.classes.all()
        if new_class in schedule:  # class is already in schedule
            return False
        if new_class.source_data["enrl_stat"] == "C":  # closed
            return False
        for each_class in schedule:
            if each_class.semester != new_class.semester:
                return False
            if classes_overlap(
                each_class, new_class
            ):  # class conflicts with one already in schedule
                return False
            if (
                each_class.subject == new_class.subject
                and each_class.catalog_number == new_class.catalog_number
                and each_class.component == new_class.component
            ):  # same course, different section (e.g. two lectures for the same class)
                return False
        return True

    def add_class(self, new_class):
        if self.class_can_be_added(new_class):
            self.classes.add(new_class)
        else:
            raise Exception("Course cannot be added.")

    def remove_class(self, old_class):
        if old_class in self.classes.all():
            self.classes.remove(old_class)
        else:
            raise Exception("Course is not in schedule.")

    def reset_advisor(self):
        self.approved = None
        self.save()
