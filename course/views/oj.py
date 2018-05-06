from utils.api import APIView,validate_serializer

from ..models import CourseAnnouncement, Course,UserCourse,Course_task,Taskproblem,TaskSmallproblem,CourseSubmission
from problem.serializers import ProblemAdminSerializer,SmallProblemSerializer,ProblemSerializer
from ..serializers import CourseAnnouncementSerializer,CourseSerializer,CourseTaskSerializer\
    ,CourseSubmissionModelSerializer,CourseSubmissionSafeModelSerializer,CreateCourseSubmissionSerializer
from problem.models import Problem,SmallProblem,SmallJudgeStatus,ProblemRuleType
import logging
logger = logging.getLogger("django")
from django.db import transaction#2018.3.15
from utils.captcha import Captcha
from utils.throttling import TokenBucket
from utils.cache import cache
from options.options import SysOptions
from judge.dispatcher import CourseJudgeDispatcher

class CourseAnnouncementListAPI(APIView):
    def get(self, request):
        course_id = request.GET.get("course_id")
        if not course_id:
            return self.error("Invalid parameter, course_id is required")
        data = CourseAnnouncement.objects.select_related("created_by").filter(course_id=course_id, visible=True)
        return self.success(CourseAnnouncementSerializer(data, many=True).data)


class CourseAPI(APIView):
    def post(self,request):
        data = request.data
        user = request.user
        try:
            course = Course.objects.get(code=data["code"])
        except Course.DoesNotExist:
            return self.error("课程不存在")
        user_courses = UserCourse.objects.filter(user=user)
        for user_course in user_courses:
            if user_course.course==course:
                return self.error("该课程已加入...")
        with transaction.atomic():
            UserCourse.objects.create(user=user,course=course)
            course.total_student = course.total_student + 1
            course.save()
        return self.success()

    def get(self, request):
        user = request.user
        id = request.GET.get("course_id")#课程id

        if id:
            course = Course.objects.get(id=id)
            return self.success(CourseSerializer(course).data)
        userCourse = UserCourse.objects.filter(user=user)
        return self.success([CourseSerializer(data.course).data for data in userCourse])

    def delete(self,request):
        user = request.user
        course_id = request.GET.get("course_id")
        UserCourse.objects.filter(course_id=course_id,user=user).delete()
        return self.success()


class CourseTaskAPI(APIView):
    def get(self,request):
        task_id = request.GET.get("task_id")
        if task_id:
            task = Course_task.objects.get(id=task_id)
            return self.success(CourseTaskSerializer(task).data)

        id = request.GET.get("course_id")  # 课程id
        task  = Course_task.objects.filter(course_id=id,visible=True)
        return self.success(CourseTaskSerializer(task,many=True).data)#如果是根据表连接查询得到的数据，要在上many=Ture.


class CourseTaskProblemAPI(APIView):
    @staticmethod
    def _add_two_problem_status(request, queryset_values1,queryset_values2):
        if request.user.is_authenticated:
            user = request.user
            course_id = request.GET.get("course_id")
            task_id = request.GET.get("task_id")
            user_course = UserCourse.objects.get(course_id=course_id,user=user)

            for small_problem in queryset_values1:
                small_problem["my_status"] = user_course.small_problem_status.get(str(task_id), {}).get(str(small_problem["id"]), {}).get("status")
                small_problem["my_answer"] = user_course.small_problem_status.get(str(task_id), {}).get(str(small_problem["id"]), {}).get("answer")
            for problem in queryset_values2:
                if problem["rule_type"] == ProblemRuleType.ACM:
                    problem["my_status"] = user_course.acm_problem_status.get(str(task_id), {}).get(str(problem["id"]), {}).get("status")
                else:
                    problem["my_status"] = user_course.oi_problem_status.get(str(task_id), {}).get(str(problem["id"]), {}).get("status")

    @staticmethod
    def _add_problem_status(request, queryset_values):
        if request.user.is_authenticated:
            user = request.user
            course_id = request.GET.get("course_id")
            task_id = request.GET.get("task_id")
            user_course = UserCourse.objects.get(course_id=course_id,user=user)

            if queryset_values["rule_type"] == ProblemRuleType.ACM:
                queryset_values["my_status"] = user_course.acm_problem_status.get(str(task_id), {}).get(str(queryset_values["id"]), {}).get("status")
            else:
                queryset_values["my_status"] = user_course.oi_problem_status.get(str(task_id), {}).get(str(queryset_values["id"]), {}).get("status")

    def get(self,request):
        # 问题详情页
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by") \
                    .get(id=problem_id, is_public=True, visible=True)
                problem_data = ProblemSerializer(problem).data#serializer序列化是把从数据库得到的QuerySet对象转化为python可以识别的dict数据类型
                self._add_problem_status(request,problem_data)
                return self.success(problem_data)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")
        task_id = request.GET.get("task_id")
        task = Course_task.objects.get(id=task_id)
        problems = Taskproblem.objects.filter(task=task)
        small_problems =TaskSmallproblem.objects.filter(task=task)
        data1 = [SmallProblemSerializer(smallproblem.smallproblem).data for smallproblem in small_problems]
        data2 = [ProblemAdminSerializer(problem.problem).data for problem in problems]
        self._add_two_problem_status(request,data1,data2)
        return self.success_new(data1,data2)

class JudgeSmallProblemAPI(APIView):#判断小题
    def post(self, request):
        data = request.data
        user_id = request.user.id
        problem_id = data["id"]
        course_id = data["course_id"]
        task_id = data["task_id"]
        my_answer = data["my_answer"]#用户答案
        small_problem = SmallProblem.objects.get(id=problem_id)
        if small_problem.answer == my_answer:
            result = SmallJudgeStatus.TRUE
        else:
            result = SmallJudgeStatus.FALSE
        #往user_course加小题做题状态
            # update_usercourse
        user_course = UserCourse.objects.get(course_id=course_id,user_id=user_id)
        small_problem_status = user_course.small_problem_status
        if task_id not in small_problem_status:
            small_problem_status[task_id]={}
        small_problem_status[task_id][problem_id] = {"status": result, "answer": my_answer}
        user_course.small_problems_status = small_problem_status
        user_course.save()
        return self.success({"my_status":result})

class JudgeProblemAPI(APIView):#判断编程题
    def throttling(self, request):
        user_bucket = TokenBucket(key=str(request.user.id),
                                  redis_conn=cache, **SysOptions.throttling["user"])
        can_consume, wait = user_bucket.consume()
        if not can_consume:
            return "Please wait %d seconds" % (int(wait))

        ip_bucket = TokenBucket(key=request.session["ip"],
                                redis_conn=cache, **SysOptions.throttling["ip"])
        can_consume, wait = ip_bucket.consume()
        if not can_consume:
            return "Captcha is required"

    @validate_serializer(CreateCourseSubmissionSerializer)
    def post(self, request):
        data = request.data
        hide_id = False
        course_id = data["course_id"]
        task_id = data["task_id"]


        if data.get("captcha"):
            if not Captcha(request).check(data["captcha"]):
                return self.error("Invalid captcha")
        error = self.throttling(request)
        if error:
            return self.error(error)

        try:
            problem = Problem.objects.get(id=data["problem_id"], visible=True)
        except Problem.DoesNotExist:
            return self.error("Problem not exist")
        #更新题目提交状态2018.3.14
        submission = CourseSubmission.objects.create(user_id=request.user.id,
                                               username=request.user.username,
                                               language=data["language"],
                                               code=data["code"],
                                               problem_id=problem.id,
                                               ip=request.session["ip"])
        # use this for debug
        CourseJudgeDispatcher(submission.id, problem.id,course_id,task_id).judge()
        #judge_task.delay(submission.id, problem.id)#2018.2.4
        if hide_id:
            return self.success()
        else:
            return self.success({"submission_id": submission.id})


class CourseSubmissionAPI(APIView):
    def get(self, request):
        submission_id = request.GET.get("id")
        if not submission_id:
            return self.error("Parameter id doesn't exist")
        try:
            submission = CourseSubmission.objects.select_related("problem").get(id=submission_id)
        except CourseSubmission.DoesNotExist:
            return self.error("Submission doesn't exist")

        if submission.problem.rule_type == ProblemRuleType.OI or request.user.is_admin_role():
            submission_data = CourseSubmissionModelSerializer(submission).data
        else:
            submission_data = CourseSubmissionSafeModelSerializer(submission).data
        # 是否有权限取消共享
        submission_data["can_unshare"] = submission.check_user_permission(request.user, check_share=False)
        return self.success(submission_data)
