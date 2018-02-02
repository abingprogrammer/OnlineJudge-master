from __future__ import absolute_import, unicode_literals
from celery import shared_task
from judge.dispatcher import JudgeDispatcher


@shared_task
def judge_task(submission_id, problem_id):#存放判题服务器队列，然后自行调度运行代码
    JudgeDispatcher(submission_id, problem_id).judge()#dispatcher调度 2018.1.31
