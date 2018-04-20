from django.conf.urls import url

from ..views.admin import CourseAPI, CourseAnnouncementAPI, CourseTaskAPI, CourseMemberAPI

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_admin_api"),
    url(r"^course/announcement/?$", CourseAnnouncementAPI.as_view(), name="course_announcement_admin_api"),
    url(r"^course/task/?$", CourseTaskAPI.as_view(), name="course_task_admin_api"),
    url(r"^course/member/?$", CourseMemberAPI.as_view(), name="course_member_admin_api"),
]
