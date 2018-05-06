from django.conf.urls import url

from ..views.oj import CourseAPI, CourseAnnouncementListAPI, CourseTaskAPI,\
    CourseTaskProblemAPI,JudgeSmallProblemAPI,JudgeProblemAPI,CourseSubmissionAPI

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_api"),
    url(r"^course/add?$", CourseAPI.as_view(), name="course_add_api"),
    url(r"^course/exit?$", CourseAPI.as_view(), name="course_exit_api"),
    url(r"^course/announcement?$", CourseAnnouncementListAPI.as_view(), name="course_announcement_api"),
    url(r"^course/task?$", CourseTaskAPI.as_view(), name="course_task_api"),
    url(r"^course/task/problem?$", CourseTaskProblemAPI.as_view(), name="course_task_problem_api"),
    url(r"^course/task/submit_small ?$", JudgeSmallProblemAPI.as_view(), name="course_judge_small_problem_api"),
    url(r"^course/task/submit?$", JudgeProblemAPI.as_view(), name="course_judge_problem_api"),
    url(r"^course/task/submission?$", CourseSubmissionAPI.as_view(), name="course_judge_problem_api"),
]
