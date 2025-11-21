from django.db import models
from django.urls import reverse

# A Django model is a table in your database.
# Create your models here.

class Members(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    designation = models.CharField(max_length=255,default='Developer')
    image = models.ImageField(upload_to='images')
    #image_id = models.ForeignKey(MemberImage, on_delete=models.CASCADE )
   # image_id = models.CharField(max_length=20, default= "")

    #Upon creating this object return to list view for this object
    def get_absolute_url(self):
        return reverse('members_list')

    def __str__(self):
        return self.firstname

class Courses(models.Model):
    CATEGORY = [('P',"Programming"), ('W',"Web Development"), ('D',"DataAnalysis"), ('O',"DevOps"), ('T',"Testing"), ('X',"Others")]
    coursename = models.CharField(max_length=255)
    facultyname = models.ForeignKey(Members, on_delete=models.CASCADE)
    startdate = models.DateTimeField(blank = 'True')
    enddate = models.DateTimeField(blank= 'True')
    category=models.CharField(max_length=255, choices=CATEGORY)
#    # teachers = models.ManyToManyField(Members)

    # Upon creating this object return to list view for this object
    #This method can also be part of ,<object>CreateView
    def get_absolute_url(self):
        return reverse('courses_list')

    def __str__(self):
        return self.coursename

class Student(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    doj = models.DateTimeField(blank= True)
    resume = models.URLField(null = True, blank = True, default= "")
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    skills = models.TextField(max_length=255, null = True,blank = True,  default = "")
    email = models.EmailField(max_length=100, null = True, blank = True, default= "")

    def __str__(self):
        return self.firstname

class User(models.Model):
    username =  models.CharField(max_length=255)
    password =  models.CharField(max_length=255)
    email = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to='images', null = True )