from django.shortcuts import render, redirect
from .models import Parent, Child, Lesson, Teacher
from django.forms.models import model_to_dict
from . import models
import datetime
from django.contrib import messages
import bcrypt
from django.template.loader import render_to_string
from django.http import JsonResponse


def login_registration(request):
    return render(request, "signup_login.html")


def register(request):
    if request.POST['option'] == "parent":
        password = request.POST['password']
        pw_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()).decode()
        errors = models.parent_validator(
            request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
                return redirect('/')
        user = models.add_parent(request.POST, request.FILES, pw_hash)
        models.add_child(request.POST, user.id)
        if 'user_id' not in request.session:
            request.session['type'] = "parent"
            request.session['user_id'] = user.id
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
            return redirect('/parent-profile/'+str(request.session['user_id']))
    if request.POST['option'] == "teacher":
        password = request.POST['password']
        pw_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()).decode()
        errors = models.parent_validator(
            request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
                return redirect('/')
        user = models.add_teacher(request.POST, request.FILES, pw_hash)
        if 'user_id' not in request.session:
            request.session['type'] = "teacher"
            request.session['user_id'] = user.id
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
            return redirect('/teacher-profile/'+str(request.session['user_id']))


def login(request):
    if request.POST['options'] == "parent":
        email = request.POST['email']
        user = models.get_parent(email)
        if user == 1:
            messages.error(request, "You are not a parent!")
            return redirect("/")
        if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
            if user is not None:
                if 'user_id' not in request.session:
                    request.session['type'] = "parent"
                    request.session['user_id'] = user.id
                    request.session['first_name'] = user.first_name
                    request.session['last_name'] = user.last_name
                return redirect('/home/')
    if request.POST['options'] == "teacher":
        email = request.POST['email']
        user = models.get_teacher(email)
        if user == 1:
            messages.error(request, "You are not a teacher!")
            return redirect("/")
        if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
            if user is not None:
                if 'user_id' not in request.session:
                    request.session['type'] = "teacher"
                    request.session['user_id'] = user.id
                    request.session['first_name'] = user.first_name
                    request.session['last_name'] = user.last_name
                return redirect('/teacher-profile/'+str(request.session['user_id']))
    return redirect('/')


def logout(request):
    del request.session['user_id']
    del request.session['first_name']
    del request.session['last_name']
    del request.session['type']
    return redirect('/')


def parent_profile(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in to view this page")
    if request.session['user_id'] != int(id) and request.session['type'] == "parent":
        return redirect("/parent-profile/"+str(request.session['user_id']))
    parent = Parent.objects.get(id=id)
    children = parent.children.all()
    all_lessons = []
    for child in children:
        all_lessons.append(Lesson.objects.filter(child=child.id))
    context = {
        "parent": parent,
        "children": children,
        "all_lessons": all_lessons
    }
    return render(request, "parent_profile.html", context)


def teacher_profile(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in to view this page")
    if request.session['user_id'] != int(id) and request.session['type'] == "teacher":
        return redirect("/parent-profile/"+str(request.session['user_id']))
    teacher = Teacher.objects.get(id=id)
    students = teacher.lessons.all()
    all_lessons_for_each_student = []
    all_teacher_lessons = Lesson.objects.filter(
        teacher=Teacher.objects.get(id=id))
    for lesson in all_teacher_lessons:
        if lesson.child is None:
            print(lesson.child)
            continue
        print(lesson.child)
        all_lessons_for_each_student.append(lesson)
    print(all_lessons_for_each_student)
    context = {
        "teacher": teacher,
        "students": students,
        "all_teacher_lessons": all_teacher_lessons,
        "all_lessons": all_lessons_for_each_student,
    }
    if request.session['type'] == "parent":
        parent = Parent.objects.get(id=request.session['user_id'])
        children = parent.children.all()
        context['children'] = children
    return render(request, "teacher_profile.html", context)


def add_lesson(request, id):
    errors = models.lesson_validator(
        request.POST, id)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
            return redirect('/teacher-profile/'+str(id))
    models.add_lesson(request.POST, id)
    return redirect('/teacher-profile/'+str(id))


def add_child_form(request, d, n, tid):
    parent = Parent.objects.get(id=request.session['user_id'])
    children = parent.children.all()
    all_teacher_lessons = Lesson.objects.filter(
        teacher=Teacher.objects.get(id=tid), time=n, day=d)
    context = {
        'children': children,
        "d": d,
        "n": n,
        "tid": tid,
        "teacher_lesson": all_teacher_lessons
    }
    return render(request, "schedule_day.html", context)


def signup_to_lesson(request, id, d, n, tid):
    child = Child.objects.get(id=request.POST['child'])
    teacher = Teacher.objects.get(id=tid)
    available = models.child_is_available(day=d, time=n, child=child)
    available_2 = models.is_lesson_available(day=d, time=n, id=tid)
    if available and available_2:
        lesson = Lesson.objects.get(teacher=teacher, day=d, time=n)
        lesson.child = child
        lesson.save()
    elif not available:
        messages.error(request, "You are not available at this time!")
        return redirect('/teacher-profile/add-to-lesson/'+str(d)+"/"+str(n)+"/"+str(tid))
    elif not available_2:
        messages.error(request, "Teacher is not available at this time!")
        return redirect('/teacher-profile/add-to-lesson/'+str(d)+"/"+str(n)+"/"+str(tid))
    return redirect('/teacher-profile/'+str(tid))


def home(request):
    context = {}
    url_parameter = request.GET.get("q")
    print(url_parameter)
    if url_parameter:
        teachers = Teacher.objects.filter(first_name__icontains=url_parameter)
        teacher_subject = Teacher.objects.filter(
            specialization__icontains=url_parameter)
    else:
        teachers = Teacher.objects.all()
        teacher_subject = Teacher.objects.all()
    context['teachers'] = teachers
    context['specialization'] = teacher_subject
    if request.is_ajax():
        html = render_to_string(
            template_name="search.html",
            context={
                "teachers": teachers,
                "specialization": teacher_subject
            }
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)

    return render(request, "home_page.html", context)


def all_lessons(request):
    Lesson.objects.all()
    context = {
        'all_lessons': Lesson.objects.all()
    }
    return render(request, 'lessons.html', context)
