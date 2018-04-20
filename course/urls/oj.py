from django.conf.urls import url

from ..views.oj import CourseListAPI, CourseAPI

urlpatterns = [
    url(r"^courses/?$", CourseListAPI.as_view(), name="course_list_api"),
    url(r"^course/?$", CourseAPI.as_view(), name="course_api"),
    #url(r"^course/add?$", CourseAddAPI.as_view(), name="course_add_api"),
]
