from rest_framework import viewsets
from .models import Members, Courses, Student, User
from .serializers import (
    MemberSerializer, CourseSerializer,
    StudentSerializer, UserSerializer
)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Members.objects.all()
    serializer_class = MemberSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Courses.objects.all()
    serializer_class = CourseSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
