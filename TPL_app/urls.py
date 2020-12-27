from django.urls import path
from . import views
urlpatterns = [
    path('', views.login_registration),
    path('register', views.register),
    path('parent-profile/<int:id>', views.parent_profile),
    path('teacher-profile/<int:id>', views.teacher_profile),
    path('home/teacher-profile/<int:id>', views.teacher_profile),
    path('home/parent-profile/teacher-profile/<int:id>', views.teacher_profile),
    path('home/teacher-profile/teacher-profile/<int:id>', views.teacher_profile),
    path('logout', views.logout),
    path('login', views.login),
    path('add_lesson/<int:id>', views.add_lesson),
    path('teacher-profile/add-to-lesson/<str:d>/<int:n>/<int:tid>',
         views.add_child_form),
    path('home/teacher-profile/add-to-lesson/<str:d>/<int:n>/<int:tid>',
         views.add_child_form),
    path('add_child_to_lesson/<int:id>/<str:d>/<int:n>/<int:tid>',
         views.signup_to_lesson),
    path('home/', views.home),
    path('lessons', views.all_lessons),
    path('home/teacher-profile/parent-profile/<int:id>', views.parent_profile),
    path('teacher-profile/parent-profile/<int:id>', views.parent_profile),
    path('home/parent-profile/<int:id>', views.parent_profile)
]
