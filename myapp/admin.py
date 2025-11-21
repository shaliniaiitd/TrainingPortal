from django.contrib import admin

# Register your models here.
from .models import Members, Courses, Student

admin.site.register(Members)
admin.site.register(Courses)
admin.site.register(Student)