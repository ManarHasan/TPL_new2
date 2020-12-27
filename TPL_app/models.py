from django.db import models
import time
from datetime import datetime, date
from django import forms
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')


class Teacher(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, null=True)
    email = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    profile_pic = models.ImageField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Parent(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    profile_pic = models.ImageField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Child(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    grade = models.IntegerField()
    parent = models.ForeignKey(
        Parent, related_name="children", on_delete=models.CASCADE)
    lessons = models.ManyToManyField(
        Teacher, through="Lesson", related_name="lessons")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    style = models.CharField(max_length=255, null=True)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, blank=True, null=True)
    day = models.CharField(max_length=255, null=True)
    time = models.CharField(max_length=255, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def add_parent(postData, postFiles, pw_hash):
    if len(postFiles) < 1:
        postFiles['pic'] = "images/profile_pic.png"
    user = Parent.objects.create(
        first_name=postData['fname'], last_name=postData['lname'], occupation=postData['occupation'], email=postData['email'], password=pw_hash, profile_pic=postFiles['pic'])
    return user


def add_child(postData, user_id):
    for i in range(int(postData['number_of_children'])):
        child = Child.objects.create(first_name=postData[f'child_name{i}'], last_name=postData['lname'],
                                     age=postData[f'age{i}'], grade=postData[f'grade{i}'], parent=Parent.objects.get(id=user_id))
    return child


def add_teacher(postData, postFiles, pw_hash):
    if len(postFiles) < 1:
        postFiles['pic'] = "images/profile_pic.png"
    user = Teacher.objects.create(
        first_name=postData['fname'], last_name=postData['lname'], occupation=postData['occupation'], email=postData['email'], gender=postData['gender'], password=pw_hash, specialization=postData['specialization'], education=postData['education'], profile_pic=postFiles['pic'])
    return user


def add_lesson(postData, id):
    lesson = Lesson.objects.create(title=postData['title'], description=postData['description'],
                                   price=postData['price'], style=postData['style'], day=postData['day'], time=postData['time'], teacher=Teacher.objects.get(id=id))
    return lesson


def get_parent(email):
    user = Parent.objects.filter(email=email)
    if len(user) < 1:
        return 1
    return user[0]


def get_teacher(email):
    user = Teacher.objects.filter(email=email)
    if len(user) < 1:
        return 1
    return user[0]


def is_duplicate_email(email):
    parent = Parent.objects.filter(email=email).values()
    if len(parent):
        return True
    return False


def validate_text(text, min_length=2):
    if text.isalpha == False:
        return 0
    elif len(text) < min_length:
        return 1
    elif len(text) > min_length:
        return 2


def validate_email(email):
    regex = re.compile(r'^[a-zA-Z0-9.+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]+$')
    if re.search(regex, email):
        if not is_duplicate_email(email):
            return 2
        return 1
    return 0


def teacher_validator(postData):
    errors = {}
    if validate_text(postData['fname']) == 0:
        errors["first_name"] = "You must enter a name"
    if validate_text(postData['fname']) == 1:
        errors["fname_length"] = "first name is too short"
    if validate_text(postData['lname']) == 0:
        errors["last_name"] = "You must enter a last name"
    # if validate_text(postData["lname"]) == 1:
    #     errors["lname_length"] = "last name is too short"
    if validate_text(postData['occupation']) == 0:
        errors["occupation"] = "You must enter your occupation information"
    if validate_text(postData['occupation']) == 1:
        errors["occupation_length"] = "the data you entered is too short"
    if validate_text(postData['specialization']) == 0:
        errors["specialization"] = "You must enter your specialization info"
    if validate_text(postData['specialization']) == 1:
        errors["specialization_length"] = "the data you entered is too short"
    return errors


def parent_validator(postData):
    errors = {}
    if validate_text(postData['fname']) == 1:
        errors["fname"] = "This name is too short!"
    if validate_text(postData['fname']) == 0:
        errors["fname_letters"] = "A name must be Abc characters only! Sorry Elon Musk!"
    if validate_text(postData['lname']) == 1:
        errors["lname"] = "This name is too short!"
    if validate_text(postData['lname']) == 0:
        errors["lname_letters"] = "A name must be Abc characters only!"
    if validate_email(postData['email']) == 0:
        errors["email"] = "Invalid email"
    if validate_email(postData['email']) == 1:
        errors["email_exists"] = "This email already exists"
    if validate_text(postData['password'], min_length=8) == 1:
        errors["password"] = "Password is too short!"
    if validate_text(postData['occupation'], min_length=5) == 1:
        errors["occupation"] = "Occupation must be at least 5 charcters"
    return errors


def child_validator(postData):
    errors = {}
    if validate_text(postData['fname']) == 1:
        errors["fname"] = "This name is too short!"
    if validate_text(postData['fname']) == 0:
        errors["fname_letters"] = "A name must be Abc characters only! Sorry Elon Musk!"
    return errors


def is_available(day, time, id):
    lessons = Lesson.objects.filter(
        day=day, time=time, teacher=Teacher.objects.get(id=id))
    print(lessons)
    if len(lessons) > 0:
        return False
    return True


def is_lesson_available(day, time, id):
    lessons = Lesson.objects.filter(
        day=day, time=time, teacher=Teacher.objects.get(id=id))
    print(lessons)
    print(lessons[0].child)
    if lessons[0].child is None:
        return True
    return False


def child_is_available(child, day, time):
    lessons = Lesson.objects.filter(day=day, time=time, child=child)
    print(lessons)
    if len(lessons) > 0:
        return False
    return True


def lesson_validator(postData, id):
    errors = {}
    if len(postData['title']) < 2:
        errors['title'] = "Title should have at least many characters"
    if validate_text(postData['description'], min_length=5) == 1:
        errors['description'] = "Description  should have at least 5 characters"
    if is_available(postData['day'], postData['time'], id) == False:
        errors['time'] = "You already have a lesson at this time!"
    return errors
