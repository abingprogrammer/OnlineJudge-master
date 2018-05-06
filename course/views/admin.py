import dateutil.parser

from utils.api import APIView, validate_serializer

from account.decorators import ensure_created_by
from ..models import Course, CourseAnnouncement, Course_task, UserCourse,Taskproblem,TaskSmallproblem
from account.models import User
from ..serializers import (CourseAdminSerializer, CreateCourseSeriaizer, EditCourseSeriaizer,
                           CourseAnnouncementSerializer, CreateCourseAnnouncementSerializer, EditCourseAnnouncementSerializer,
                           CourseTaskSerializer, ImportUserSeralizer,ImageUploadForm, CreateCourseTaskSerializer,
                           )
import os
from utils.shortcuts import rand_str
from django.conf import settings
from problem.models import Problem,SmallProblem
from problem.serializers import CreateCourseProblemSerializer,CreateCourseSmallProblemSerializer,EditCourseProblemSerializer,EditCourseSmallProblemSerializer,ProblemAdminSerializer,SmallProblemSerializer
from problem.views.admin import ProblemBase
from django.db import transaction#2018.3.15
from utils.encryption import Course_code
import logging
logger = logging.getLogger("django")

class CourseAPI(APIView):
    request_parsers = ()
    def post(self, request):
        #上传图片
        form = ImageUploadForm(request.POST)
        data = form.data#Querydict对象
        course_data = dict()
        avatar = request.FILES.get('image')
        if avatar:
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
        if data["id"]:  # 存在id，则修改课程
            course = Course.objects.get(id=data["id"])
            for k, v in course_data.items():
                setattr(course, k, v)  # 把json格式数据一一赋值到course对象
                course.save()
            return self.success(CourseAdminSerializer(course).data)
        else:

            course = Course.objects.create(**course_data)
            course.code= Course_code.encryption(course.id)  # 生成课程代码
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

    def delete(self,request):
        course_id = request.GET.get("id")
        Course.objects.filter(id=course_id).delete()
        return self.success()



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
    @validate_serializer(CreateCourseTaskSerializer)
    def post(self,request):#增加作业单元，所需参数：course_id、total_task、作业单元的属性
        data = request.data
        data['created_by'] = request.user

        course_id = data.pop('course_id')
        data['course'] = Course.objects.get(id=course_id)#外键
        course_task = Course_task.objects.create(**data)
        return self.success(CourseTaskSerializer(course_task).data)

    def get(self,request):
        course_id = request.GET.get("course_id")
        course = Course.objects.get(id=course_id)
        tasks = Course_task.objects.filter(course=course)
        return self.success(self.paginate_data(request, tasks, CourseTaskSerializer))

    def put(self,request):
        data = request.data

        task_id = data["task_id"]
        task = Course_task.objects.get(id=task_id)

        for k, v in data.items():
            setattr(task, k, v)
            task.save()
        return self.success()

    def delete(self,request):
        course_id = request.GET.get("course_id")
        course = Course.objects.get(id=course_id)
        task_id = request.GET.get("task_id")
        Course_task.objects.filter(id=task_id,course=course).delete()
        return self.success()


class CourseMemberAPI(APIView):
    @validate_serializer(ImportUserSeralizer)
    def post(self,request):#可以通过用户名或邮箱查找用户，这里选择用户名
        data = request.data
        course_id = data["course_id"]
        course = Course.objects.get(id=course_id)
        total_student = course.total_student

        users = data["students"]
        for username in users:
            user= User.objects.get(username=username)
            if not user:
                return self.error("User does not exist!")
            UserCourse.objects.create(course=course,user=user)
            total_student = total_student+1

        course.total_student = total_student
        course.save()
        return self.success()

    def get(self, request):
        course_id = request.GET.get("course_id")
        course = Course.objects.get(id=course_id)
        #data = list()
        #for id in course.student_id:
        users = UserCourse.objects.filter(course=course)
        data = list()

        for user in users:
            student = User.objects.get(id=user.user_id)
            message = dict()
            message["id"] = student.id
            message["username"] = student.username
            message["email"] = student.email
            data.append(message)

        #data.append(user)
        return self.success(data)

    def put(self, request):
        data = request.data
        course_id = data["course_id"]
        students = data["student_id"]#学生的id
        course = Course.objects.get(id=course_id)
        total_student = course.total_student
        for student in students:
            user = User.objects.get(id=student)
            UserCourse.objects.filter(user=user,course=course).delete()
            total_student = total_student-1
        course.total_student = total_student
        course.save()
        return self.success()


#单元题目列表
class CourseTaskProblemListAPI(APIView):
    def get(self,request):
        task_id = request.GET.get("task_id")
        task = Course_task.objects.get(id=task_id)
        problems = Taskproblem.objects.filter(task=task)
        small_problems =TaskSmallproblem.objects.filter(task=task)
        return self.success_new([SmallProblemSerializer(smallproblem.smallproblem).data for smallproblem in small_problems],
                    [ProblemAdminSerializer(problem.problem).data for problem in problems])
        # small_problems = task.small_problem
        # data = list()
        # try:
        #     for id in problems:
        #         message = dict()
        #         problem = Problem.objects.get(id=id)
        #         message["id"] = id
        #         message["title"] = problem.title
        #         message["type"] = None
        #         message["visible"] = problem.visible
        #         message["is_public"] = problem.is_public
        #         data.append(message)
        # except Problem.DoesNotExist:
        #     return self.error("problem is not exist")
        #
        # try:
        #     for id in small_problems:
        #         message = dict()
        #         small_problem = SmallProblem.objects.get(id=id)
        #         message["id"] = id
        #         message["title"] = small_problem.title
        #         message["type"] = small_problem.type
        #         message["visible"] = small_problem.visible
        #         message["is_public"] = small_problem.is_public
        #         data.append(message)
        # except SmallProblem.DoesNotExist:
        #     return self.error("smallProblem is not exist")


    def put(self,request):#删除单元列表中题目
        data = request.data
        problem_id = data["problem_id"]
        task_id = data["task_id"]
        is_problem = data["is_problem"]
        if is_problem:
            with transaction.atomic():
                Taskproblem.objects.filter(task_id=task_id,problem_id=problem_id).delete()
                Problem.objects.filter(id=problem_id).delete()
        else:
            with transaction.atomic():
                TaskSmallproblem.objects.filter(task_id=task_id, smallproblem_id=problem_id).delete()
                SmallProblem.objects.filter(id=problem_id).delete()
        return self.success()



#从公共习题加入题目
class AddCourseProblemAPI(APIView):
    def post(self,request):
        data=request.data
        task_id = data["task_id"]

        ids = data["problem_id"]
        is_problem = data["is_problem"]
        #多个字段筛选是编程题还是小题
        if is_problem:
            for id in ids:
                Taskproblem.objects.create(problem_id=id, task_id=task_id)
        else:
            for id in ids:
                TaskSmallproblem.objects.create(smallproblem_id=id, task_id=task_id)
        return self.success()

#课程单元创建编程题
class CourseTaskProblemAPI(ProblemBase):
    @validate_serializer(CreateCourseProblemSerializer)
    def post(self, request):
        data = request.data
        task_id = data.pop("task_id")
        task = Course_task.objects.get(id=task_id)

        error_info = self.common_checks(request)
        if error_info:
            return self.error(error_info)
        with transaction.atomic():
            problem = Problem.objects.create(**data)
            Taskproblem.objects.create(task=task,problem=problem)

        return self.success()

    @validate_serializer(EditCourseProblemSerializer)
    def put(self,request):
        data = request.data
        problem_id = data.pop("id")

        try:
            problem = Problem.objects.get(id=problem_id)
            ensure_created_by(problem, request.user)
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")

        error_info = self.common_checks(request)
        if error_info:
            return self.error(error_info)
        # todo check filename and score info
        data["languages"] = list(data["languages"])

        for k, v in data.items():
            setattr(problem, k, v)
        problem.save()
        return self.success()


#课程单元创建小题
class CourseTaskSmallProblemAPI(APIView):
    @validate_serializer(CreateCourseSmallProblemSerializer)
    def post(self,request):
        data = request.data
        data["created_by"] = request.user#获取当前用户
        task_id = data.pop("task_id")
        task = Course_task.objects.get(id=task_id)
        with transaction.atomic():
            small_problem = SmallProblem.objects.create(**data)
            TaskSmallproblem.objects.create(task=task,smallproblem=small_problem)
        return self.success()

    @validate_serializer(EditCourseSmallProblemSerializer)
    def put(self,request):
        data = request.data
        problem_id = data.pop("id")

        try:
            problem = SmallProblem.objects.get(id=problem_id)
            ensure_created_by(problem, request.user)
        except SmallProblem.DoesNotExist:
            return self.error("Problem does not exist")
        for k, v in data.items():
            setattr(problem, k, v)
        problem.save()

        return self.success()