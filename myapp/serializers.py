from rest_framework import serializers
from .models import Members, Courses, Student, User

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Members
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    # Show faculty details inside course API
    facultyname = MemberSerializer(read_only=True)
    facultyname_id = serializers.PrimaryKeyRelatedField(
        queryset=Members.objects.all(), source='facultyname', write_only=True
    )

    class Meta:
        model = Courses
        fields = ['id', 'coursename', 'facultyname', 'facultyname_id',
                  'startdate', 'enddate', 'category']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
