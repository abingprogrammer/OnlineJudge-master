import dateutil.parser

from utils.api import APIView, validate_serializer

from account.decorators import ensure_created_by
from ..models import Course, CourseAnnouncement, Course_task
from account.models import User
from ..serializers import (CourseAdminSerializer, CreateCourseSeriaizer, EditCourseSeriaizer,
                           CourseAnnouncementSerializer, CreateCourseAnnouncementSerializer, EditCourseAnnouncementSerializer,
                           CourseTaskSerializer, ImportUserSeralizer,ImageUploadForm,CourseMemberSeralizer)
import os
from utils.shortcuts import rand_str
from django.conf import settings
import logging

logger = logging.getLogger("django")

class CourseAPI(APIView):
    request_parsers = ()
    #@validate_serializer(CreateCourseSeriaizer)
    def post(self, request):
        #上传图片
        form = ImageUploadForm(request.POST)
        data = form.data#Querydict对象
        #data = form.clean()
        #logger.debug(form.is_valid())
        #logger.debug(data)
        # logger.debug(form.cleaned_data["image"])
        #if form.is_valid():
            #logger.debug(data)
        course_data = dict()
        avatar = request.FILES.get('image')
        if avatar:
            #logger.debug(avatar)
            # else:
            #     return self.error("Invalid file content")
            if avatar.size > 2 * 1024 * 1024:
                return self.error("Picture is too large")
            suffix = os.path.splitext(avatar.name)[-1].lower()
            if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
                return self.error("Unsupported file format")

            name = rand_str(10) + suffix
            with open(os.path.join(settings.COURSE_DIR, name), "wb") as img:
                for chunk in avatar:
                    img.write(chunk)
            course_data["picture"] = f"{settings.COURSE_PREFIX}/{name}"

        course_data["start_time"] = dateutil.parser.parse(data["start_time"])
        course_data["end_time"] = dateutil.parser.parse(data["end_time"])
        if course_data["end_time"] <= course_data["start_time"]:
            return self.error("Start time must occur earlier than end time")
        course_data["created_by"] = request.user

        course_data["title"] = data["title"]
        course_data["introduction"] = data["introduction"]
        course_data["visible"] = data["visible"]

        course = Course.objects.create(**course_data)
        return self.success(CourseAdminSerializer(course).data)

    @validate_serializer(EditCourseSeriaizer)
    def put(self, request):
        data = request.data
        try:
            course = Course.objects.get(id=data.pop("id"))
            ensure_created_by(course, request.user)#验证该课程是否被当前用户创建的
        except Course.DoesNotExist:
            return self.error("Course does not exist")
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        if data["end_time"] <= data["start_time"]:
            return self.error("Start time must occur earlier than end time")

        for k, v in data.items():
            setattr(course, k, v)#把json格式数据一一赋值到course对象
            course.save()
        return self.success(CourseAdminSerializer(course).data)

    def get(self, request):
        course_id = request.GET.get("id")
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                ensure_created_by(course, request.user)
                return self.success(CourseAdminSerializer(course).data)
            except Course.DoesNotExist:
                return self.error("Course does not exist")

        courses = Course.objects.all().order_by("-create_time")
        if request.user.is_admin():
            courses = courses.filter(created_by=request.user)

        return self.success(self.paginate_data(request, courses, CourseAdminSerializer))


class CourseAnnouncementAPI(APIView):
    @validate_serializer(CreateCourseAnnouncementSerializer)
    def post(self, request):
        """
        Create one course_announcement.
        """
        data = request.data
        try:
            course = Course.objects.get(id=data.pop("course_id"))
            ensure_created_by(course, request.user)
            data["course"] = course
            data["created_by"] = request.user
        except Course.DoesNotExist:
            return self.error("Course does not exist")
        announcement = CourseAnnouncement.objects.create(**data)
        return self.success(CourseAnnouncementSerializer(announcement).data)

    @validate_serializer(EditCourseAnnouncementSerializer)
    def put(self, request):
        """
        update course_announcement
        """
        data = request.data
        try:
            course_announcement = CourseAnnouncement.objects.get(id=data.pop("id"))
            ensure_created_by(course_announcement, request.user)
        except CourseAnnouncement.DoesNotExist:
            return self.error("Course announcement does not exist")
        for k, v in data.items():
            setattr(course_announcement, k, v)
            course_announcement.save()
        return self.success()

    def delete(self, request):
        """
        Delete one course_announcement.
        """
        course_announcement_id = request.GET.get("id")
        if course_announcement_id:
            if request.user.is_admin():
                CourseAnnouncement.objects.filter(id=course_announcement_id,
                                                   course__created_by=request.user).delete()
            else:
                CourseAnnouncement.objects.filter(id=course_announcement_id).delete()
        return self.success()

    def get(self, request):
        """
        Get one course_announcement or course_announcement list.
        """
        course_announcement_id = request.GET.get("id")
        if course_announcement_id:
            try:
                course_announcement = CourseAnnouncement.objects.get(id=course_announcement_id)
                ensure_created_by(course_announcement, request.user)
                return self.success(CourseAnnouncementSerializer(course_announcement).data)
            except CourseAnnouncement.DoesNotExist:
                return self.error("Contest announcement does not exist")

        course_id = request.GET.get("course_id")
        if not course_id:
            return self.error("Parameter error")
        course_announcements = CourseAnnouncement.objects.filter(course_id=course_id)
        if request.user.is_admin():
            course_announcements = course_announcements.filter(created_by=request.user)
        keyword = request.GET.get("keyword")
        if keyword:
            course_announcements = course_announcements.filter(title__contains=keyword)
        return self.success(CourseAnnouncementSerializer(course_announcements, many=True).data)


class CourseTaskAPI(APIView):
    def post(self,request):#增加作业单元，所需参数：course_id、total_task、作业单元的属性
        data = request.data
        data['created_by'] = request.user

        course_id = data.pop('course_id')
        data['course'] = Course.objects.get(id=course_id)#外键

        tasks = data.pop["total_task"]#作业单元序号
        data['task_id'] = tasks+1

        course_task = Course_task.objects.create(**data)
        return self.success(CourseTaskSerializer(course_task).data)


class CourseMemberAPI(APIView):
    @validate_serializer(ImportUserSeralizer)
    def post(self,request):#可以通过用户名或邮箱查找用户，这里选择用户名
        data = request.data
        course_id = data["course_id"]
        course = Course.objects.get(id=course_id)
        total_student = course.total_student

        users = data["name"]
        for user in users:
            user_id = User.objects.values('id').filter(username=user)
            if not user_id:
                return self.error("User does not exist!")
            course.student_id.append(user_id)
            total_student = total_student+1

        course.total_student = total_student
        course.save()
        return self.success()

    def get(self, request):
        course_id = request.GET.get("course_id")
        course = Course.objects.get(id=course_id)
        #data = list()
        for id in course.student_id:
            users = User.objects.filter()
            #data.append(user)
        return self.success(self.paginate_data(request, users, CourseMemberSeralizer))

    def delete(self, request):
        data = request.data
        course_id = data["course_id"]
        students = data["students"]#学生的id
        course = Course.objects.get(id = course_id)
        students_id = course.student_id
        for id in students:
            students_id.pop(id)
        return self.success()
