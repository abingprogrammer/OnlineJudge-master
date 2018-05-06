import random
from django.db.models import Q, Count
from utils.api import APIView
from account.decorators import login_required, check_contest_permission
from ..models import ProblemTag, Problem, ProblemRuleType, SmallProblem, SmallTag, SmallJudgeStatus
from ..serializers import ProblemSerializer, TagSerializer, ProblemSafeSerializer, SmallProblemSerializer, SmallTagSerializer
from contest.models import ContestRuleType
from django.db import transaction#2018.3.15
from account.models import User
import logging
logger = logging.getLogger("django")
class ProblemTagAPI(APIView):
    def get(self, request):#annotate括号里使用聚合函数，这里用Count统计次数2018.1.30
        tags = ProblemTag.objects.annotate(problem_count=Count("problem")).filter(problem_count__gt=0)
        return self.success(TagSerializer(tags, many=True).data)

#2018.3.11
class SmallTagAPI(APIView):
    def get(self, request):#annotate括号里使用聚合函数，这里用Count统计次数2018.1.30
        tags = SmallTag.objects.annotate(smallproblem_count=Count("smallproblem")).filter(smallproblem_count__gt=0)
        return self.success(SmallTagSerializer(tags, many=True).data)

class PickOneAPI(APIView):
    def get(self, request):
        problems = Problem.objects.filter(contest_id__isnull=True, visible=True)
        count = problems.count()
        if count == 0:
            return self.error("No problem to pick")
        return self.success(problems[random.randint(0, count - 1)]._id)


class ProblemAPI(APIView):
    @staticmethod
    def _add_problem_status(request, queryset_values):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            acm_problems_status = profile.acm_problems_status.get("problems", {})
            oi_problems_status = profile.oi_problems_status.get("problems", {})
            # paginate data
            results = queryset_values.get("results")
            if results is not None:
                problems = results
            else:
                problems = [queryset_values, ]
            for problem in problems:
                if problem["rule_type"] == ProblemRuleType.ACM:
                    problem["my_status"] = acm_problems_status.get(str(problem["id"]), {}).get("status")
                else:
                    problem["my_status"] = oi_problems_status.get(str(problem["id"]), {}).get("status")

    def get(self, request):
        # 问题详情页
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by") \
                    .get(_id=problem_id, is_public=True, visible=True)
                problem_data = ProblemSerializer(problem).data#serializer序列化是把从数据库得到的QuerySet对象转化为python可以识别的dict数据类型
                self._add_problem_status(request, problem_data)
                return self.success(problem_data)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        limit = request.GET.get("limit")
        if not limit:
            return self.error("Limit is needed")

        problems = Problem.objects.select_related("created_by").filter(is_public=True, visible=True)
        # 按照标签筛选
        tag_text = request.GET.get("tag")
        if tag_text:
            problems = problems.filter(tags__name=tag_text)

        # 搜索的情况
        keyword = request.GET.get("keyword", "").strip()
        if keyword:
            problems = problems.filter(Q(title__icontains=keyword) | Q(_id__icontains=keyword))

        # 难度筛选
        difficulty = request.GET.get("difficulty")
        if difficulty:
            problems = problems.filter(difficulty=difficulty)
        #标页数
        data = self.paginate_data(request, problems, ProblemSerializer)
        # 根据profile 为做过的题目添加标记
        self._add_problem_status(request, data)
        return self.success(data)

#2018.3.10
class SmallProblemAPI(APIView):
    @staticmethod
    def _add_problem_status(request, queryset_values):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            small_problems_status = profile.small_problems_status.get("smallproblems", {})
            # paginate data
            results = queryset_values.get("results")
            if results is not None:
                problems = results
            else:
                problems = [queryset_values, ]
            for problem in problems:
                problem["my_status"] = small_problems_status.get(str(problem["id"]), {}).get("status")
                problem["my_answer"] = small_problems_status.get(str(problem["id"]), {}).get("answer")

    def get(self,request):
        # 问题详情页
        small_problem_id = request.GET.get("small_problem_id")
        if small_problem_id:
            try:
                small_problem = SmallProblem.objects.select_related("created_by") \
                    .get(_id=small_problem_id, is_public=True, visible=True)
                small_problem_data = SmallProblemSerializer(small_problem).data#serializer序列化是把从数据库得到的QuerySet对象转化为python可以识别的dict数据类型
                #self._add_problem_status(request, problem_data)
                return self.success(small_problem_data)
            except SmallProblem.DoesNotExist:
                return self.error("Problem does not exist")

        limit = request.GET.get("limit")
        if not limit:
            return self.error("Limit is needed")

        small_problem = SmallProblem.objects.select_related("created_by").filter(is_public=True,visible=True)

        #标签筛选
        tag_text = request.GET.get("tag")
        if tag_text:
            small_problem = small_problem.filter(tags__name=tag_text)

        #关键词
        keyword = request.GET.get("keyword","").strip()
        if keyword:
            small_problem = small_problem.filter(Q(title__icontains=keyword))

        #小题类型筛选
        type = request.GET.get("type")
        if type:
            small_problem = small_problem.filter(type=type)

        #分页
        data = self.paginate_data(request, small_problem, SmallProblemSerializer)
        # 根据profile 为做过的题目添加标记
        self._add_problem_status(request, data)
        return self.success(data)

#2018.3.14
class JudgeSmallProblemAPI(APIView):#判断小题
    @login_required
    def post(self, request):
        data = request.data
        user_id = request.user.id
        id = data["id"]
        my_answer = data["my_answer"]#用户答案
        small_problem = SmallProblem.objects.get(id=id)
        if small_problem.answer == my_answer:
            result = SmallJudgeStatus.TRUE
        else:
            result = SmallJudgeStatus.FALSE
        #往user_profile加小题做题状态,并更新提交和通过数量
        with transaction.atomic():
            #update small_problem
            small_problem = SmallProblem.objects.select_for_update().get(id=id)
            small_problem.submission_number += 1
            if result == SmallJudgeStatus.TRUE:
                small_problem.accepted_number += 1
            small_problem_info = small_problem.statistic_info
            small_problem_info[result] = small_problem_info.get(result, 0) + 1

            small_problem.save(update_fields=["accepted_number", "submission_number", "statistic_info"])

            # update_userprofile
            user = User.objects.select_for_update().get(id=user_id)
            user_profile = user.userprofile
            user_profile.submission_number += 1
            small_problems_status = user_profile.small_problems_status.get("smallproblems", {})
            if result == SmallJudgeStatus.TRUE:
                user_profile.accepted_number += 1
            small_problems_status[id] = {"status":result,"_id":id, "answer":my_answer}
            user_profile.small_problems_status["smallproblems"] = small_problems_status
            user_profile.save(update_fields=["submission_number", "accepted_number", "small_problems_status"])
        return self.success({"my_status":result})


class ContestProblemAPI(APIView):
    def _add_problem_status(self, request, queryset_values):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            if self.contest.rule_type == ContestRuleType.ACM:
                problems_status = profile.acm_problems_status.get("contest_problems", {})
            else:
                problems_status = profile.oi_problems_status.get("contest_problems", {})
            for problem in queryset_values:
                problem["my_status"] = problems_status.get(str(problem["id"]), {}).get("status")

    @check_contest_permission(check_type="problems")
    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by").get(_id=problem_id,
                                                                           contest=self.contest,
                                                                           visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist.")
            if self.contest.problem_details_permission(request.user):
                problem_data = ProblemSerializer(problem).data
                self._add_problem_status(request, [problem_data, ])
            else:
                problem_data = ProblemSafeSerializer(problem).data
            return self.success(problem_data)

        contest_problems = Problem.objects.select_related("created_by").filter(contest=self.contest, visible=True)
        if self.contest.problem_details_permission(request.user):
            data = ProblemSerializer(contest_problems, many=True).data
            self._add_problem_status(request, data)
        else:
            data = ProblemSafeSerializer(contest_problems, many=True).data
        return self.success(data)
