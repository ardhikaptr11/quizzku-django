"""
URL configuration for the onlinecourse application.

This module defines the URL patterns for the onlinecourse app, mapping URLs to their corresponding views.
It includes routes for course listing, user registration, login, logout, course details, enrollment,
submission, and exam results. The urlpatterns list routes URLs to views, and the static function is used
to serve media files during development.

Routes:
- "" : CourseListView for displaying the list of courses.
- "<int:pk>/" : CourseDetailView for displaying course details.
- "registration/" : registration_request for user registration.
- "login/" : login_request for user login.
- "logout/" : logout_request for user logout.
- "enroll/<int:course_id>/" : enroll for enrolling in a course.
- "<int:course_id>/submit/" : submit for submitting course work.
- "course/<int:course_id>/submission/<int:submission_id>/result/" : show_exam_result for displaying exam results.

Static files are served using settings.MEDIA_URL and settings.MEDIA_ROOT.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

# Application namespace
app_name = "onlinecourse"

urlpatterns = [
    path(route="", view=views.CourseListView.as_view(), name="index"),
    path(route="<slug:course_slug>/enroll/", view=views.enroll, name="enroll"),
    path(route="<slug:course_slug>/", view=views.CourseDetailView.as_view(), name="course_details"),
    path(route="<slug:course_slug>/lesson/", view=views.start_quiz, name="quiz_page"),
    path(route="<slug:course_slug>/lesson/submit/", view=views.submit, name="submit"),
    path(
        route="<slug:course_slug>/lesson/result/",
        view=views.show_exam_result,
        name="exam_result",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# path(route="<int:course_id>/lesson/<int:lesson_id>/submit/", view=views.submit, name="submit"),
# path(
#     route="onlinecourse/quiz/<int:course_id>/lesson/result/",
#     view=views.show_exam_result,
#     name="exam_result",
# ),
# enroll/<int:course_id>/
# quiz/<int:pk>/
# route="quiz/<int:course_id>/lesson/<int:lesson_id>/result/",
# path('onlinecourse/quiz/<int:quiz_id>/lesson/result/', views.quiz_result, name='quiz_result')
# http://localhost:8000/onlinecourse/exam/1/lesson/1/result?submission=1
# http://localhost:8000/onlinecourse/quiz/4/lesson/result?name=Javascript+Fundamental&attempt=1
