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
# List of valid URL patterns
urlpatterns = [
    path(route="", view=views.CourseListView.as_view(), name="index"),
    path(route="<int:pk>/", view=views.CourseDetailView.as_view(), name="course_details"),
    path(route="registration/", view=views.registration_request, name="registration"),
    path(route="login/", view=views.login_request, name="login"),
    path(route="logout/", view=views.logout_request, name="logout"),
    path(route="enroll/<int:course_id>/", view=views.enroll, name="enroll"),
    path(route="quiz/<int:course_id>/lesson/", view=views.start_exam, name="quiz_page"),
    path(route="quiz/<int:course_id>/lesson/<int:lesson_id>/submit/", view=views.submit, name="submit"),
    # path(route="<int:course_id>/submit/", view=views.submit, name="submit"),
    path(
        route="quiz/<int:course_id>/submission/<int:submission_id>/",
        view=views.show_exam_result,
        name="exam_result",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# http://localhost:8000/onlinecourse/exam/1/lesson/1/result?submission=1
