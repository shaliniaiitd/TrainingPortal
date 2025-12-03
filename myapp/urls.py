from django.urls import path, include
from . import views
from rest_framework import routers
from .api_views import (
    MemberViewSet, CourseViewSet,
    StudentViewSet, UserViewSet
)

router = routers.DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'students', StudentViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', views.index, name='index'),

    # UI Views
    path('courses/', views.CoursesListView.as_view(), name='courses_list'),
    path('members/', views.MembersListView.as_view(), name='members_list'),
    path('courses/addcourse/', views.CourseCreateView.as_view(), name='addcourse'),
    path('courses/<pk>/detail/', views.CourseDetailView.as_view(), name='courses_detail'),
    path('members/detail/<pk>', views.MemberDetailView.as_view(), name='members_detail'),
    path('members/addmember/', views.MemberCreateView.as_view(), name='addmember'),
    path('members/delete/<pk>', views.MemberDeleteView.as_view(), name='delete'),
    path('members/update/<pk>', views.MemberUpdateView.as_view(), name='update'),
    path('courses/<pk>/delete/', views.CourseDeleteView.as_view(), name='deletec'),
    path('courses/update/<pk>', views.CourseUpdateView.as_view(), name='updatecourse'),

    # API routes
    path('api_sync/', include(router.urls)),
]
