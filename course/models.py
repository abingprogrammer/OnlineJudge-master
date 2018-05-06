from django.db import models
from utils.models import JSONField

from account.models import User
from utils.models import RichTextField
from django.conf import settings
from problem.models import Problem,SmallProblem
from utils.shortcuts import rand_str
from submission.models import JudgeStatus

class Course(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 创建课程的老师
    total_student = models.IntegerField(default=0, blank=True)

    title = models.CharField(max_length=64)
    introduction = RichTextField()
    #contents = RichTextField(null=True)
    picture = models.CharField(max_length=256,default=f"{settings.COURSE_PREFIX}/default.png")
    code = models.CharField(max_length=32)

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
        unique_together = (("code"),)  # 设置唯一

class Course_task(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    introduction = RichTextField()
    #type = models.CharField(max_length=32)#作业类型，作业或练习task\practice
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

class Taskproblem(models.Model):
    task = models.ForeignKey(Course_task,on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)

    class Meta:
        db_table = "task_problem"

class TaskSmallproblem(models.Model):
    task = models.ForeignKey(Course_task,on_delete=models.CASCADE)
    smallproblem = models.ForeignKey(SmallProblem,on_delete=models.CASCADE)

    class Meta:
        db_table = "task_small_problem"

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

class UserCourse(models.Model):
    user = models.ForeignKey(User,verbose_name='用户',on_delete=models.CASCADE)
    course = models.ForeignKey(Course,verbose_name='课程',on_delete=models.CASCADE)
    create_time = models.DateTimeField('添加时间', auto_now_add=True)
    acm_problem_status = JSONField(default=dict())
    oi_problem_status = JSONField(default=dict())
    small_problem_status = JSONField(default=dict())
    class Meta:
        db_table = "user_course"
        ordering = ("-create_time",)

class TaskType(object):
    TASK="task"
    PRACTICE="practice"

class CourseSubmission(models.Model):
    id = models.CharField(max_length=32, default=rand_str, primary_key=True, db_index=True)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(db_index=True)
    username = models.CharField(max_length=30)
    code = models.TextField()
    result = models.IntegerField(db_index=True, default=JudgeStatus.PENDING)
    # 从JudgeServer返回的判题详情
    info = JSONField(default=dict)
    language = models.CharField(max_length=20)
    shared = models.BooleanField(default=False)
    # 存储该提交所用时间和内存值，方便提交列表显示
    # {time_cost: "", memory_cost: "", err_info: "", score: 0}
    statistic_info = JSONField(default=dict)
    ip = models.CharField(max_length=32, null=True, blank=True)

    def check_user_permission(self, user, check_share=True):
        return self.user_id == user.id or \
               (check_share and self.shared is True) or \
               user.is_super_admin() or \
               user.can_mgmt_all_problem() or \
               self.problem.created_by_id == user.id

    class Meta:
        db_table = "course_submission"
        ordering = ("-create_time",)

    def __str__(self):
        return self.id