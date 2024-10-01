"""
This module contains view functions and class-based views for the online course application.
It handles user registration, login, logout, course enrollment, exam submission, and displaying exam results.
The module also includes utility functions to check user enrollment status and extract submitted answers from HTTP requests.

`Functions`:

    registration_request(request: HttpRequest) -> HttpResponse:
        Handles user registration requests, processes both GET and POST requests for user registration.

    login_request(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
        Handles user login requests, processes login requests, and authenticates users.

    logout_request(request: HttpRequest) -> HttpResponseRedirect:
        Handles user logout requests, logs out the current user, and redirects to the index page.

    check_if_enrolled(user: User, course: Course) -> bool:
        Checks if a user is enrolled in a given course.

    enroll(request: HttpRequest, course_id: int) -> HttpResponseRedirect:
        Handles course enrollment requests, creates an enrollment record if the user is not already enrolled.

    submit(request: HttpRequest, course_id: int) -> HttpResponseRedirect:

    extract_answers(request: HttpRequest) -> List[int]:

    show_exam_result(request: HttpRequest, course_id: int, submission_id: int) -> HttpResponse:
        Displays the exam result for a specific course and submission.

`Classes`:

    CourseListView(generic.ListView):
        Displays a list of courses, ordered by total enrollment.

    CourseDetailView(generic.DetailView):
        Displays the details of a specific course.

"""

import logging
from typing import List

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

# Import models
from .models import Course, Enrollment, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request: HttpRequest) -> HttpResponse:
    """
    Handles user registration requests.
    This view function processes both GET and POST requests for user registration.
    For GET requests, it renders the user registration template.
    For POST requests, it attempts to create a new user with the provided username,
    password, first name, and last name. If the username already exists, it returns
    an error message indicating that the user already exists.
    Args:
        request (HttpRequest): The HTTP request object containing request data.
    Returns:
        HttpResponse: The HTTP response object with the rendered template or a redirect
        to the index page upon successful registration.
    """

    # Context is a dictionary that is passed to the template
    context = {}

    if request.method == "GET":
        return render(request, "onlinecourse/user_registration_bootstrap.html", context)
    elif request.method == "POST":
        # Send POST request from retrieved username, password, first name, and last name
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        # Set initial state for user existence
        user_exist = False

        # Error handling for user existence
        # Change the state if the user already exists
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            logger.error("New user")

        # Create a new user if the user does not exist, otherwise return an error message
        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context["message"] = "User already exists."
            return render(request, template_name="onlinecourse/user_registration_bootstrap.html", context=context)


def login_request(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    """
    Handle user login requests.
    This view function processes login requests. If the request method is POST, it attempts to
    authenticate the user with the provided username and password. If authentication is successful,
    the user is logged in and redirected to the index page. If authentication fails, an error message
    is added to the context and the login page is re-rendered. For GET requests, the login page is
    rendered without any context.
    Args:
        request (HttpRequest): The HTTP request object containing request data.
    Returns:
        HttpResponse: The HTTP response object with the rendered login page or a redirect to the index page.
    """

    context = {}
    if request.method == "POST":
        # Send POST request from retrieved username and password, and send them to the authenticate function
        username = request.POST["username"]
        password = request.POST["psw"]
        user = authenticate(username=username, password=password)  # Authenticate function to athenticate the user

        # Check if user is authenticated
        # Redirect to index page if user is authenticated, otherwise return an error message in the login page
        if user is not None:
            login(request, user)
            return redirect(to="onlinecourse:index")
        else:
            context["message"] = "Invalid username or password."
            return render(request, template_name="onlinecourse/user_login_bootstrap.html", context=context)
    else:
        return render(request, template_name="onlinecourse/user_login_bootstrap.html", context=context)


def logout_request(request: HttpRequest) -> HttpResponseRedirect:
    """
    Handle the user logout request.
    This view function logs out the current user and redirects them to the index page of the online course application.
    Args:
        request (HttpRequest): The HTTP request object that triggered this view.
    Returns:
        HttpResponseRedirect: A redirect response to the index page of the online course application.
    """

    logout(request)
    return redirect(to="onlinecourse:index")


def check_if_enrolled(user: User, course: Course) -> bool:
    """
    Check if a user is enrolled in a given course.
    This function checks if the given user is enrolled in the specified course by querying the Enrollment
    model. If the user is enrolled, it returns True; otherwise, it returns False.
    Args:
        user (User): The user object to check enrollment for.
        course (Course): The course object to check enrollment in.
    Returns:
        bool: True if the user is enrolled in the course, False otherwise.
    """

    # Set initial state
    is_enrolled = False

    if user.id is not None:
        # Check if user enrolled, if user is enrolled the num of results will not be 0
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# Generic class-based views
class CourseListView(generic.ListView):
    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by("-total_enrollment")[:10]  # Get the top 10 courses based on total enrollment
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = "onlinecourse/course_detail_bootstrap.html"


def enroll(request: HttpRequest, course_id: int) -> HttpResponseRedirect:
    course = get_object_or_404(Course, pk=course_id)  # Get the Course object based on the course_id
    user = request.user

    # Helper function to check if the user is enrolled
    is_enrolled = check_if_enrolled(user, course)

    # Create an enrollment if the user is authenticated and not enrolled
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode="honor")
        course.total_enrollment += 1
        course.save()

    # Redirect to the course details page if the user is authenticated and enrolled
    if user.is_authenticated and is_enrolled:
        return HttpResponseRedirect(reverse(viewname="onlinecourse:course_details", args=(course.id,)))

    # Redirect to the login page if the user is not authenticated
    return HttpResponseRedirect(reverse(viewname="onlinecourse:login"))


# Create a submit view to create an exam submission record for a course enrollment
def submit(request: HttpRequest, course_id: int) -> HttpResponseRedirect:
    """
    Handles the submission of an exam for a specific course by a user.
    The function retrieves the course and user information, gets the corresponding enrollment object,
    creates a submission object, associates the selected choices with the submission, and redirects
    to the exam result page.
    Args:
        request (HttpRequest): The HTTP request object containing user data and form data.
        course_id (int): The ID of the course for which the exam is being submitted.
    Returns:
        HttpResponseRedirect: A redirect response to the exam result page with the course ID and submission ID.
    """

    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    # Get the Enrollment object for the user and course
    enrollment = Enrollment.objects.get(user=user, course=course)
    # Create Submission object for the enrollment
    submission = Submission.objects.create(enrollment=enrollment)
    submission_id = submission.id
    # Associate selected choices with the submission
    choices = extract_answers(request)
    submission.choices.set(choices)
    return HttpResponseRedirect(reverse(viewname="onlinecourse:exam_result", args=(course_id, submission_id)))


# A method to collect the selected choices from the exam form from the request object
def extract_answers(request: HttpRequest) -> List[int]:
    """
    Extracts submitted answers from an HTTP POST request.
    This function iterates over the keys in the POST data of the given request,
    identifies keys that start with "choice", and extracts their corresponding
    values. The values are converted to integers and collected into a list,
    which represents the IDs of the submitted choices.
    Args:
        request (HttpRequest): The HTTP request object containing POST data.
    Returns:
        List[int]: A list of integers representing the IDs of the submitted choices.
    """

    submitted_anwsers = []
    for key in request.POST:
        if key.startswith("choice"):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    return submitted_anwsers


# Create an exam result view to check if learner passed exam and show their question results and result for each question
def show_exam_result(request: HttpRequest, course_id: int, submission_id: int) -> HttpResponse:
    """
    Display the exam result for a specific course and submission.
    The function retrieves the course and submission objects based on the provided IDs. It then calculates the total
    score by comparing the selected choices with the correct choices for each question in the course. The context
    dictionary is populated with the course, total score, and selected choices, and the exam result page is rendered
    using this context.
    Args:
        request (HttpRequest): The HTTP request object.
        course_id (int): The ID of the course.
        submission_id (int): The ID of the submission.
    Returns:
        HttpResponse: The HTTP response with the rendered exam result page.
    """

    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    # Get QuerySet of selected choices for the submission
    choices = submission.choices.all()
    total_score = 0
    # Get QuerySet of questions for the course
    questions = course.question_set.all()

    # Calculate total score by comparing selected choices with correct choices for each question
    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)
        selected_choices = choices.filter(question=question)
        # Score will be added if the selected choice matches the correct choice
        if set(selected_choices) == set(correct_choices):
            total_score += question.grade

    # Add courses, total scores, and choices to the context dictionary for further use within the template
    context["course"] = course
    context["grade"] = total_score
    context["choices"] = choices

    return render(request, template_name="onlinecourse/exam_result_bootstrap.html", context=context)
