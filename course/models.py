from django.db import models
from utils.models import JSONField

from account.models import User
from utils.models import RichTextField
from django.conf import settings

class Course(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 创建课程的老师
    student_id = JSONField(default=list)
    total_student = models.IntegerField(default=0, blank=True)
    total_task = models.IntegerField(default=0, blank=True)

    title = models.CharField(max_length=64)
    introduction = RichTextField()
    #contents = RichTextField(null=True)
    picture = models.CharField(max_length=256,default=f"{settings.COURSE_PREFIX}/default.png")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    # 是否可见 false的话相当于删除
    visible = models.BooleanField(default=True)

    # @property
    # def status(self):
    #     if self.start_time > now():
    #         # 没有开始 返回1
    #         return CourseStatus.COURSE_NOT_START
    #     elif self.end_time < now():
    #         # 已经结束 返回-1
    #         return CourseStatus.COURSE_ENDED
    #     else:
    #         # 正在进行 返回0
    #         return CourseStatus.COURSE_UNDERWAY
    class Meta:
        db_table = "course"
        ordering = ("create_time",)

class Course_task(models.Model):
    course_id = models.ForeignKey(Course,on_delete=models.CASCADE)
    task_id = models.IntegerField()
    title = models.CharField(max_length=64)
    introduction = RichTextField()
    type = models.CharField(max_length=32)#作业类型，作业或练习task\practice
    visible = models.BooleanField(default=True)

    problem = JSONField(default=list)
    small_problem = JSONField(default=list)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_task"
        ordering = ("create_time",)

class CourseAnnouncement(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    content = RichTextField()
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_announcement"
        ordering = ("-create_time",)