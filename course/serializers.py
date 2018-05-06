from utils.api import UsernameSerializer, serializers
from .models import Course, Course_task, CourseAnnouncement,CourseSubmission
from django import forms
from judge.languages import language_names

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

    id = serializers.IntegerField()
    title = serializers.CharField(max_length=64)
    introduction = serializers.CharField()
    #picture = serializers.CharField(max_length=256)

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

    class Meta:
        model = Course_task
        fields = "__all__"


class CreateCourseTaskSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    title = serializers.CharField(max_length=128)
    #type = serializers.ChoiceField(choices=[TaskType.TASK,TaskType.PRACTICE])
    introduction = serializers.CharField(allow_blank=True, allow_null=True)

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    # 是否可见 false的话相当于删除
    visible = serializers.BooleanField(default=True)

#课程添加用户
class ImportUserSeralizer(serializers.Serializer):
    course_id = serializers.IntegerField()
    students = serializers.ListField(child=serializers.CharField(max_length=32))

class CreateCourseSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = serializers.ChoiceField(choices=language_names)
    code = serializers.CharField(max_length=20000)
    course_id = serializers.IntegerField()
    task_id = serializers.IntegerField()
    captcha = serializers.CharField(required=False)

class CourseSubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseSubmission
        fields = "__all__"

# 不显示submission info的serializer, 用于ACM rule_type
class CourseSubmissionSafeModelSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")

    class Meta:
        model = CourseSubmission
        exclude = ("info", "ip")
