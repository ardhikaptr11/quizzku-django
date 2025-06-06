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

import json
import logging
import random

# import re
from datetime import date
from typing import List

# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth import get_user_model
from django.db.models import Count, Max, Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from account.models import User

# Import models
from .models import Attempt, Course, Enrollment, Lesson, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
        num_results = Enrollment.objects.filter(learner=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# Generic class-based views
class CourseListView(generic.ListView):
    model = Course
    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            username = user.username
            fullname = getattr(user, "full_name", None)

            if not fullname:
                return redirect(reverse("account:complete_profile") + f"?username={username}")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user
        course_age = {}
        context = super().get_context_data(**kwargs)

        for course in context["course_list"]:
            last_created = date.today() - course.pub_date
            course_age[course.id] = last_created.days

        context["completion_percentage"] = user.completion_percentage() if user.is_authenticated else 0
        context["course_age"] = course_age
        context["attempt_limit"] = self.request.session.get("attempt_limit", False)
        context["from_registration"] = self.request.session.get("from_registration", False)

        return context

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
    slug_field = "slug_name"
    slug_url_kwarg = "course_slug"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("account:getting_started")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.get_object()
        lessons = course.lessons.all()

        lesson_attempts = {}

        for lesson in lessons:
            attempt = Attempt.objects.filter(learner=user, lesson=lesson).last()
            if attempt:
                lesson_attempts[lesson.id] = attempt.remaining_attempts
            else:
                lesson_attempts[lesson.id] = lesson.total_attempt

        context["completion_percentage"] = user.completion_percentage() if user.is_authenticated else 0
        context["lesson_attempts"] = lesson_attempts
        return context


def enroll(request: HttpRequest, course_slug: str) -> HttpResponse | HttpResponseRedirect:
    user = request.user
    course = get_object_or_404(Course, slug_name=course_slug)  # Get the Course object based on the course_id

    # Helper function to check if the user is enrolled
    is_enrolled = check_if_enrolled(user, course)

    if request.method == "GET":
        # Create an enrollment if the user is authenticated and not enrolled
        if not is_enrolled and user.is_authenticated:
            Enrollment.objects.create(learner=user, course=course, mode="honor")
            course.total_enrollment += 1
            course.save()
            return HttpResponseRedirect(reverse(viewname="onlinecourse:course_details", args=(course_slug,)))

        # Redirect to the course details page if the user is authenticated and enrolled
        if user.is_authenticated and is_enrolled:
            return HttpResponseRedirect(reverse(viewname="onlinecourse:course_details", args=(course_slug,)))

        # Redirect to the login page if the user is not authenticated
        # return render(
        #     request,
        #     template_name="getting_started.html",
        #     context={"not_authenticated": "Oops! You're not logged in."},
        # )


def start_quiz(request: HttpRequest, course_slug) -> HttpResponse:
    user = request.user

    # Filter user's enrollment for specific course
    enrollment = user.enrollments.filter(course__slug_name=course_slug)

    # Get the total number of attempts for a user on a particular lesson in the course.
    total_attempts = (
        enrollment.aggregate(
            total_attempts=Count("course__lessons__attempts", filter=Q(course__lessons__attempts__learner=user))
        )["total_attempts"]
        or 0
    )

    # When the user is not logged in, render the getting_started page with a warning message
    if request.method == "GET" and not user.is_authenticated:
        return render(
            request,
            template_name="getting_started.html",
            context={"not_authenticated": "Oops! You're not logged in."},
        )

    # When the user is logged in and already attempted the quiz 3 times, prevent them from attempting the quiz again
    # This will keep the attempt data consistent, where no user has more than 3 attempts on a lesson
    elif request.method == "GET" and total_attempts == 3 and not user.is_superuser:
        request.session["attempt_limit"] = True
        return HttpResponseRedirect(reverse(viewname="onlinecourse:index"))

    # Retrieve the course based on the course_id
    course = get_object_or_404(Course, slug_name=course_slug)

    # Retrieve the lesson name from the query parameter
    lesson_title = request.GET.get("name", "").strip()

    # Check if lesson_title is provided
    if not lesson_title:
        return HttpResponse("Lesson name is required.", status=400)

    # Find the lesson based on the lesson title and course
    lesson = get_object_or_404(Lesson, title=lesson_title, course=course)

    # Ensure that Question model has a ForeignKey to Lesson
    # Assuming Question has a ForeignKey to Lesson with related_name='questions'

    attempt = Attempt.objects.filter(learner=user, lesson=lesson)
    attempt_no = 1 if not attempt.exists() else attempt.last().attempt_no + 1
    random.seed(f"{date.today()}-{user.id}-{lesson.id}-{attempt_no}")

    questions = list(lesson.questions.prefetch_related("choices"))
    random.shuffle(questions)

    quiz_data = [{"question": question, "choices": list(question.choices.all())} for question in questions]

    for item in quiz_data:
        if len(item["choices"]) > 2:
            random.shuffle(item["choices"])

    is_binary_question = {question.id: question.choices.count() == 2 for question in questions}

    context = {
        "course": course,
        "lesson": lesson,
        "quiz_data": quiz_data,
        "is_binary_question": is_binary_question,
    }

    response = render(request, template_name="onlinecourse/quiz_page.html", context=context)
    response.set_cookie("is_binary_question", json.dumps(is_binary_question))
    print(response.cookies["is_binary_question"])
    print(response.cookies["is_binary_question"].value)

    return response


# Create a submit view to create an exam submission record for a course enrollment
def submit(request: HttpRequest, course_slug) -> HttpResponseRedirect:
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

    if request.method == "POST":
        user = request.user
        course = get_object_or_404(Course, slug_name=course_slug)

        data = json.loads(request.body)

        lesson_title = data.get("lessonTitle", "").strip()

        lesson = get_object_or_404(Lesson, title=lesson_title, course=course)

        attempts = Attempt.objects.filter(learner=user, lesson=lesson)

        if not attempts.exists():
            attempt_idx = 1
            attempt = Attempt.create_attempt(learner=user, lesson=lesson, attempt_no=attempt_idx)
            attempt.decrease_attempt()
        else:
            last_attempt = attempts.last()
            attempt_idx = last_attempt.attempt_no + 1

            if user.is_superuser:
                remaining_attempts = 3
            else:
                remaining_attempts = last_attempt.remaining_attempts - 1
                if last_attempt.attempt_no == 3:
                    return redirect("onlinecourse:index")

            attempt = Attempt.create_attempt(
                learner=user, lesson=lesson, attempt_no=attempt_idx, remaining_attempts=remaining_attempts
            )

        selected_choices = extract_answers(data)

        submission = Submission.objects.create(attempt=attempt, lesson=lesson)
        submission.choices.set(selected_choices)
        submission.save()

        quiz_result_url = (
            reverse("onlinecourse:exam_result", args=(course_slug,)) + f"?name={lesson_title}&attempt={attempt_idx}"
        )

        return JsonResponse({"success": True, "quiz_result_url": quiz_result_url}, status=200)
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


# A method to collect the selected choices from the exam form from the request object
def extract_answers(data: dict) -> List[int]:
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

    submitted_answers = []
    choices = data.get("choices", {})

    for selected_ids in choices.values():
        submitted_answers.extend([int(choice_id) for choice_id in selected_ids if choice_id.isdigit()])

    return submitted_answers


def calculate_grade(questions, choices):
    total_grade = 0
    grade_per_question = {}

    all_empty = all(not choices.filter(question=question).exists() for question in questions)

    if all_empty:
        for question in questions:
            if question.expect_multiple_answer:
                grade = 50
            else:
                grade = 0
            grade_per_question[question.id] = int(grade / 100) if grade in [0, 100] else grade / 100
            total_grade += grade
        quiz_grade = total_grade / max(questions.count(), 1)
        return quiz_grade, grade_per_question

    for question in questions:
        grade = question.grade

        selected_choices = choices.filter(question=question)
        correct_choices = question.choices.filter(is_correct=True)
        user_correct_choices = selected_choices.filter(is_correct=True)

        if question.expect_multiple_answer:
            score_if_empty = 50
            point_per_choice = grade / max(question.choices.count(), 1)
            incorrect_choices = abs(len(selected_choices) - len(user_correct_choices))

            if not selected_choices:
                grade = score_if_empty
            elif len(selected_choices) == len(correct_choices):
                grade = (
                    grade
                    if set(selected_choices) == set(correct_choices)
                    else grade - incorrect_choices * point_per_choice
                )
            elif len(selected_choices) < len(correct_choices):
                grade = score_if_empty + len(user_correct_choices) * point_per_choice
            else:
                grade = (
                    score_if_empty + len(user_correct_choices) * point_per_choice - incorrect_choices * point_per_choice
                )
        else:
            grade = grade if set(correct_choices) == set(selected_choices) else 0

        grade_per_question[question.id] = int(grade / 100) if grade in [0, 100] else grade / 100
        total_grade += grade

    quiz_grade = total_grade / max(questions.count(), 1)
    return quiz_grade, grade_per_question


def get_highest_grade(request: HttpRequest, lesson):
    user = request.user
    submission = Submission.objects.filter(lesson=lesson, attempt__learner=user)
    highest_grade = submission.aggregate(highest_grade=Max("grade"))["highest_grade"]
    return highest_grade


# Create an exam result view to check if learner passed exam and show their question results and result for each question
def show_exam_result(request: HttpRequest, course_slug) -> HttpResponse:
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

    if request.method == "GET" and not request.user.is_authenticated:
        return render(
            request,
            "getting_started.html",
            context={"not_authenticated": "Oops! You're not logged in."},
        )

    user = request.user
    attempt_index = request.GET.get("attempt")
    lesson_title = request.GET.get("name")

    if not attempt_index:
        return HttpResponse("Attempt index is required.", status=400)

    course = get_object_or_404(Course, slug_name=course_slug)
    lesson = get_object_or_404(Lesson, title=lesson_title, course=course)

    attempt = get_object_or_404(Attempt, learner=user, lesson=lesson, attempt_no=attempt_index)
    submission = get_object_or_404(Submission, attempt=attempt, lesson=lesson)
    submission_date = submission.submission_date.strftime("%Y-%m-%d")

    random.seed(f"{date.today()}-{user.id}-{lesson.id}-{attempt_index}")
    questions = lesson.questions.prefetch_related("choices")
    question_list = list(questions)
    random.shuffle(question_list)

    selected_choices = submission.choices.all()
    quiz_data = [
        {"selected_choices": selected_choices, "question": question, "choices": list(question.choices.all())}
        for question in question_list
    ]

    for item in quiz_data:
        if len(item["choices"]) > 2:
            random.shuffle(item["choices"])

    _, grade_per_question = calculate_grade(questions, selected_choices)

    # Add courses, total scores, and choices to the context dictionary for further use within the template
    context = {
        "course": course,
        "lesson": lesson,
        "quiz_data": quiz_data,
        "submission": submission,
        "grade": int(submission.grade) if submission.grade % 2 == 0 else round(submission.grade, 3),
        "question_grade": grade_per_question,
        "highest_grade": get_highest_grade(request, lesson),
        "user": user,
        "attempt_left": attempt.remaining_attempts,
        "submission_date": submission_date,
    }

    context["is_binary_question"] = {
        int(key): value for key, value in json.loads(request.COOKIES["is_binary_question"]).items()
    }

    return render(request, template_name="onlinecourse/quiz_result.html", context=context)
