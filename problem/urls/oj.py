from django.conf.urls import url

from ..views.oj import ProblemTagAPI, ProblemAPI, ContestProblemAPI, PickOneAPI, SmallProblemAPI, SmallTagAPI, JudgeSmallProblemAPI

urlpatterns = [
    url(r"^problem/tags/?$", ProblemTagAPI.as_view(), name="problem_tag_list_api"),
    url(r"^problem/?$", ProblemAPI.as_view(), name="problem_api"),
    url(r"^pickone/?$", PickOneAPI.as_view(), name="pick_one_api"),
    url(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_api"),
    url(r"^small_problem/?$", SmallProblemAPI.as_view(), name="small_problem_api"),#2018.3.10
    url(r"^small_problem/tags/?$", SmallTagAPI.as_view(), name="small_tag_list_api"),#2018.3.11
    url(r"^submitSmallProblem/?$", JudgeSmallProblemAPI.as_view(), name="judge_small_problem_api"),#2018.3.14
]
