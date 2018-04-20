from utils.api import APIView

from ..models import CourseAnnouncement, Course
from ..serializers import CourseAnnouncementSerializer
from ..serializers import CourseSerializer
from account.models import User

class CourseAnnouncementListAPI(APIView):
    def get(self, request):
        course_id = request.GET.get("course_id")
        if not course_id:
            return self.error("Invalid parameter, course_id is required")
        data = CourseAnnouncement.objects.select_related("created_by").filter(course_id=course_id, visible=True)
        return self.success(CourseAnnouncementSerializer(data, many=True).data)


class CourseAPI(APIView):
    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return self.error("Invalid parameter, id is required")
        try:
            course = Course.objects.get(id=id, visible=True)
        except Course.DoesNotExist:
            return self.error("Course does not exist")
        data = CourseSerializer(course).data
        return self.success(data)


class CourseListAPI(APIView):
    def get(self, request):
        profile = request.user.userprofile
        my_course = profile.my_course
        datas = list()
        data = dict()
        for id in my_course:
            data['id']=id
            course = Course.objects.get(id=id, visible=True)
            data['picture'] =course.picture
            data['title'] =course.title
            data['total_student'] =course.total_student
            create_by_id = course.created_by
            data['name'] = User.objects.values("real_name").filter(user_id=create_by_id)
            datas.append(data)

        return self.success(datas)

#用户自行添加课程
# class CourseAddAPI(APIView):
#     def post(self,request):
