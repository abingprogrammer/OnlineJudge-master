from utils.api import UsernameSerializer, serializers
from .models import Course, Course_task, CourseAnnouncement
from django import forms

#课程
class CreateCourseSeriaizer(serializers.Serializer):

    title = serializers.CharField(max_length=64)
    introduction = serializers.CharField()
    #picture = serializers.CharField(max_length=256,allow_empty=True)

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    # 是否可见 false的话相当于删除
    visible = serializers.BooleanField(default=True)

class EditCourseSeriaizer(serializers.Serializer):
    student_id = serializers.ListField(child=serializers.IntegerField(),allow_empty=True)
    total_student = serializers.IntegerField()
    total_task = serializers.IntegerField()

    title = serializers.CharField(max_length=64)
    introduction = serializers.CharField()
    contents = serializers.CharField()
    picture = serializers.CharField(max_length=256)
    task = serializers.ListField(child=serializers.IntegerField(),allow_empty=True)

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    # 是否可见 false的话相当于删除
    visible = serializers.BooleanField(default=True)

class CourseAdminSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()
    #status = serializers.CharField()#课程状态
    class Meta:
        model = Course
        fields = "__all__"

class CourseSerializer(CourseAdminSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class ImageUploadForm(forms.Form):
    image = forms.FileField()
    title = forms.CharField(max_length=64)
    introduction = forms.CharField()

    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()
    visible = serializers.BooleanField()

#课程公告
class CourseAnnouncementSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()

    class Meta:
        model = CourseAnnouncement
        fields = "__all__"

class CreateCourseAnnouncementSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    title = serializers.CharField(max_length=128)
    content = serializers.CharField()
    visible = serializers.BooleanField()

class EditCourseAnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=128, required=False)
    content = serializers.CharField(required=False, allow_blank=True)
    visible = serializers.BooleanField(required=False)


#课程作业单元
class CourseTaskSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()

    class Meta:
        model = Course_task
        fields = "__all__"

#课程添加用户
class ImportUserSeralizer(serializers.Serializer):
    name = serializers.ListField(child=serializers.CharField(max_length=32))

class CourseMemberSeralizer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=32)
    email = serializers.EmailField(max_length=64)