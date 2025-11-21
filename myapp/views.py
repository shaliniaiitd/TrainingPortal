from django.shortcuts import render,_get_queryset,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from .models import Members,Courses
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView,UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy

from .forms import UserImageForm
from .models import Student


def image_request(request):
  if request.method == 'POST':
    form = UserImageForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()

      # Getting the current instance object to display in the template
      img_object = form.instance

      return render(request, 'image_form.html', {'form': form, 'img_obj': img_object})
  else:
    form = UserImageForm(request.GET, request.FILES)
    if form.is_valid():
      form.save()

      # Getting the current instance object to display in the template
      img_object = form.instance

      return render(request, 'image_form.html', {'form': form, 'img_obj': img_object})
    #form = UserImageForm()

  return render(request, 'image_form.html', {'form': form})

def index(request):
    user = User(request)
    print(user.email)
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

class CoursesListView(ListView):
  model = Courses

  def get_context_data(self, *, object_list=None, **kwargs):
    context = super().get_context_data()
    return context

class CourseCreateView(CreateView):
    model = Courses
    fields = ['category', 'coursename', 'facultyname','startdate','enddate']


class CourseDetailView(DetailView):

    model = Courses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['students'] = Student.objects.filter(course_id =self.object.pk)
        return context

class CourseUpdateView(UpdateView):
  model=Courses
  fields = ['category', 'coursename', 'facultyname', 'startdate', 'enddate']
  template_name_suffix = '_update_form'


class CourseDeleteView(DeleteView):
  model = Courses
  success_url = reverse_lazy('courses_list')

class MemberDetailView(DetailView):
    model = Members

    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context ['courses'] = Courses.objects.filter(facultyname_id = self.object.pk)
      name = self.object.firstname + " " + self.object.lastname
      context['image'] = self.object.image
      #context['photo'] = MemberImage.objects.filter( name = name)
      #print(context['courses'])
      context['now'] = timezone.now()
      return context

class MemberUpdateView(UpdateView):
  model=Members
  fields = ['firstname', 'lastname', 'designation']

  template_name_suffix = '_update_form'



class MemberDeleteView(DeleteView):
  model = Members
  success_url = reverse_lazy('members_list')


class MemberCreateView(CreateView):
    model = Members
    fields = ['firstname','lastname','designation']
    #UploadImageCreateView()
    def get_absolute_url(self):

       return reverse('members_list')

class MembersListView(ListView):
    model = Members
    def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data()
      return context

def members(request):
  mymembers = Members.objects.all().values()
  template = loader.get_template('members.html')
  context = {
    'mymembers': mymembers,
  }
  return HttpResponse(template.render(context, request))


def courses(request):
  mycourses = Courses.objects.all().values()
  template = loader.get_template('courses.html')
  context = {
    'mycourses': mycourses,
  }
  return HttpResponse(template.render(context, request))


def add(request):
  template = loader.get_template('addmember.html')
  return HttpResponse(template.render({}, request))

def addmember(request):
  x = request.POST.get('first','')
  y = request.POST.get('last', '')
  z = request.POST.get('designation','')
  member = Members(firstname=x, lastname=y, designation=z)
  member.save()
  template = loader.get_template('members.html')
  context = {
    'member': member,
  }
  #return HttpResponseRedirect(reverse('index'))
  return HttpResponse(template.render(context, request))


def delete(request, id):
  member = Members.objects.get(id=id)
  member.delete()
  return HttpResponseRedirect(reverse('member_list'))

def update(request, id):
  mymember = Members.objects.get(id=id)
  template = loader.get_template('updatemember.html')
  context = {
    'mymember': mymember,
  }

  return HttpResponse(template.render(context, request))

def updatemember(request, id):
  member = Members.objects.get(id=id)
  member.firstname =   request.POST['first']

  member.lastname =   request.POST['last']
  member.designation= request.POST['designation']

  member.save()
  return HttpResponseRedirect(reverse('member_list'))

def addcourse(request):
  a = request.POST['course']
  b = request.POST['faculty']
  c = request.POST['startdate']
  d = request.POST['enddate']

  course = Courses(coursename= a, facultyname=b, startdate = c, enddate = d)
  course.save()
  return HttpResponseRedirect(reverse('course'))


def deletec(request, id):
  course = Courses.objects.get(id=id)
  course.delete()
  return HttpResponseRedirect(reverse('course'))

def updatec(request, id):
  mycourse = Courses.objects.get(id=id)
  template = loader.get_template('updatecourse.html')
  context = {
      'greeting':'1',
    'mycourse': mycourse,
  }
  return HttpResponse(template.render(context, request))

def updatecourse(request, id):
  course = Courses.objects.get(id=id)
  course.coursename =   request.POST['course']

  course.facultyname =   request.POST['faculty']
  course.startdate= request.POST['startdate']
  course.enddate= request.POST['enddate']

  course.save()
  return HttpResponseRedirect(reverse('course'))

# from django.shortcuts import get_object_or_404
# from my_project.example.models import Profile
# from rest_framework.renderers import TemplateHTMLRenderer
# from rest_framework.views import APIView
#
#
# class UserDetail(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = 'user_detail.html'
#
#     def get(self, request, pk):
#         profile = get_object_or_404(Profile, pk=pk)
#         serializer = ProfileSerializer(profile)
#         return Response({'serializer': serializer, 'profile': profile})
#
#     def post(self, request, pk):
#         profile = get_object_or_404(Profile, pk=pk)
#         serializer = ProfileSerializer(profile, data=request.data)
#         if not serializer.is_valid():
#             return Response({'serializer': serializer, 'profile': profile})
#         serializer.save()
#         return redirect('profile-list')

# def my_view(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         # Redirect to a success page.
#
#     else:
#       # Return an 'invalid login' error


