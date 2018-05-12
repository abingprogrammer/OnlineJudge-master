from django.db import models
from utils.models import JSONField

from account.models import User
from contest.models import Contest
from utils.models import RichTextField
from utils.constants import Choices


class ProblemTag(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "problem_tag"


class ProblemRuleType(Choices):
    ACM = "ACM"
    OI = "OI"


class ProblemDifficulty(object):
    High = "High"
    Mid = "Mid"
    Low = "Low"


class Problem(models.Model):
    # display ID
    _id = models.CharField(max_length=24, db_index=True)
    contest = models.ForeignKey(Contest, null=True, blank=True,on_delete=models.CASCADE)
    # for contest problem
    is_public = models.BooleanField(default=True)
    title = models.CharField(max_length=128)
    # HTML
    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = JSONField()
    test_case_id = models.CharField(max_length=32)
    # [{"input_name": "1.in", "output_name": "1.out", "score": 0}]
    test_case_score = JSONField()
    hint = RichTextField(blank=True, null=True)
    languages = JSONField()
    template = JSONField()
    create_time = models.DateTimeField(auto_now_add=True)
    # we can not use auto_now here
    last_update_time = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)#级联删除
    # ms
    time_limit = models.IntegerField()
    # MB
    memory_limit = models.IntegerField()
    # special judge related
    spj = models.BooleanField(default=False)
    spj_language = models.CharField(max_length=32, blank=True, null=True)
    spj_code = models.TextField(blank=True, null=True)
    spj_version = models.CharField(max_length=32, blank=True, null=True)
    spj_compile_ok = models.BooleanField(default=False)
    rule_type = models.CharField(max_length=32)
    visible = models.BooleanField(default=True)
    difficulty = models.CharField(max_length=32)
    tags = models.ManyToManyField(ProblemTag)#多对多关联表,会自动生成关联表
    source = models.CharField(max_length=200, blank=True, null=True)
    # for OI mode
    total_score = models.IntegerField(default=0, blank=True)
    submission_number = models.BigIntegerField(default=0)
    accepted_number = models.BigIntegerField(default=0)
    # {JudgeStatus.ACCEPTED: 3, JudgeStaus.WRONG_ANSWER: 11}, the number means count
    statistic_info = JSONField(default=dict)

    class Meta:
        db_table = "problem"
        unique_together = (("_id", "contest"),)#设置唯一
        ordering = ("create_time",)#设置排序

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])

    def add_ac_number(self):
        self.accepted_number = models.F("accepted_number") + 1
        self.save(update_fields=["accepted_number"])

#2018.3.15
class SmallJudgeStatus:
    TRUE = 0
    FALSE = 1

#2018.3.12
class SmallType(object):#小题类型
    Single = "Single"
    Multiple = "Multiple"
    Blank = "Blank"

#2018.3.10
class SmallTag(models.Model):
    name = models.CharField(max_length=30)
    class Meta:
        db_table = "small_tag"
#2018.3.10
class SmallProblem(models.Model):
    _id = models.CharField(max_length=24, db_index=True)#建立索引
    type = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    description = RichTextField()
    options = JSONField(default=list,null=True)
    answer = JSONField(default=list)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)#外键
    tags = models.ManyToManyField(SmallTag)#多对多关联表
    visible = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(blank=True, null=True)
    submission_number = models.BigIntegerField(default=0)
    accepted_number = models.BigIntegerField(default=0)
    statistic_info = JSONField(default=dict)
    is_public = models.BooleanField(default=True)
    class Meta:
        db_table = "small_problem"
        unique_together = (("_id"),)# 设置唯一
        ordering = ("create_time",)


