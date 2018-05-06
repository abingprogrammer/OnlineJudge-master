from django.conf.urls import url

from ..views.admin import CourseAPI, CourseAnnouncementAPI, CourseTaskAPI, CourseMemberAPI,CourseTaskProblemAPI,\
    AddCourseProblemAPI,CourseTaskProblemListAPI,CourseTaskSmallProblemAPI

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_admin_api"),
    url(r"^course/announcement/?$", CourseAnnouncementAPI.as_view(), name="course_announcement_admin_api"),
    url(r"^course/task/?$", CourseTaskAPI.as_view(), name="course_task_admin_api"),
    url(r"^course/member/?$", CourseMemberAPI.as_view(), name="course_member_admin_api"),
    url(r"^course/task_problem/?$", CourseTaskProblemListAPI.as_view(), name="course_task_problem_list_admin_api"),
    url(r"^course/task/problem/?$", CourseTaskProblemAPI.as_view(), name="course_task_problem_admin_api"),
    url(r"^course/task/small_problem/?$", CourseTaskSmallProblemAPI.as_view(), name="course_task_small_problem_admin_api"),
    url(r"^course/task/add_problem_from_public/?$", AddCourseProblemAPI.as_view(), name="add_course__problem_admin_api"),
]
