"""
This module defines the models for the online course application.

Models:
    `Instructor`: Represents an instructor with a user, employment status, and total learners.
    `Learner`: Represents a learner with a user, occupation, and social link.
    `Course`: Represents a course with a name, image, description, publication date, instructors, users, and total
    enrollment.
    `Lesson`: Represents a lesson with a title, order, course, and content.
    `Enrollment`: Represents an enrollment with a user, course, enrollment date, mode, and rating.
    `Question`: Represents a question with a course, question text, and grade.
    `Choice`: Represents a choice with a question, choice text, and correctness.
    `Submission`: Represents a submission with an enrollment and selected choices.
"""

import sys

# from django.contrib.auth import get_user_model
from django.utils.timezone import now

from account.models import Instructor, User

# User = get_user_model()

# Errror handling if Django module is missing or not installed
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

    # Define the models for the online course application

    # Instructor model
    # class Instructor(models.Model):
    #     """
    #     A model representing an instructor in the online course application.

    #     The Instructor model includes the following fields:

    #         user (ForeignKey): A reference to the user associated with the instructor.
    #         full_time (BooleanField): A boolean indicating whether the instructor is full-time. Defaults to True.
    #         total_learners (IntegerField): An integer representing the total number of learners taught by the instructor.

    #     Methods:

    #         __str__: Returns the username of the associated user as the string representation of the Instructor instance.
    #     """

    #     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="instructors")  # Act as a foreign key
    #     full_time = models.BooleanField(default=True)
    #     total_learners = models.IntegerField()

    #     def __str__(self):
    #         return self.user.username

    # # Learner model
    # class Learner(models.Model):
    # """
    # A model representing a learner in the online course application.

    # Attributes:
    #     STUDENT (str): Constant for student occupation.
    #     DEVELOPER (str): Constant for developer occupation.
    #     DATA_SCIENTIST (str): Constant for data scientist occupation.
    #     DATABASE_ADMIN (str): Constant for database admin occupation.
    #     OCCUPATION_CHOICES (list): List of tuples containing occupation choices.
    #     user (ForeignKey): A reference to the user associated with the learner.
    #     occupation (CharField): The occupation of the learner, with choices defined in OCCUPATION_CHOICES.
    #     social_link (URLField) : A URL to the learner's social profile.
    # """

    # Assign occupation
    # STUDENT = "student"
    # DEVELOPER = "developer"
    # DATA_SCIENTIST = "data_scientist"
    # DATABASE_ADMIN = "dba"

    # # Define occupation choices
    # OCCUPATION_CHOICES = [
    #     (STUDENT, "Student"),
    #     (DEVELOPER, "Developer"),
    #     (DATA_SCIENTIST, "Data Scientist"),
    #     (DATABASE_ADMIN, "Database Admin"),
    # ]

    # # Define model fields
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learners")  # Act as a foreign key
    # occupation = models.CharField(null=False, max_length=20, choices=OCCUPATION_CHOICES, default=STUDENT)
    # social_link = models.URLField(max_length=200)

    # def __str__(self):
    #     return f"{self.user.username}, {self.occupation}"


# Course model
class Course(models.Model):
    """
    Represents a course in the online course application.

    Attributes:
        name (CharField): The name of the course.
        image (ImageField): The image associated with the course.
        description (CharField): A brief description of the course.
        pub_date (DateField): The publication date of the course.
        instructors (ManyToManyField): The instructors teaching the course.
        users (ManyToManyField): The users enrolled in the course.
        total_enrollment (IntegerField): The total number of enrollments in the course.
        is_enrolled (bool): Indicates if the current user is enrolled in the course.
    """

    is_enrolled = False

    # Define model fields
    name = models.CharField(null=False, max_length=30, default="online course")
    slug_name = models.SlugField(unique=True)
    image = models.ImageField(upload_to="course_images/")
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    total_enrollment = models.IntegerField(default=0)
    # Define model relationships
    # Model has a many-to-many relationship with Instructor
    instructors = models.ManyToManyField(Instructor)
    # Model has a many-to-many relationship with User through Enrollment
    # In other words, it's not a direct relationship
    users = models.ManyToManyField(User, through="Enrollment", through_fields=("course", "learner"))

    def __str__(self):
        return f"Name: {self.name}, Description: {self.description}"


# Lesson model
class Lesson(models.Model):
    """
    Represents a lesson in an online course.

    Attributes:
        course (ForeignKey): A reference to the Course this lesson belongs to.
        order (IntegerField): The order of the lesson within the course.
        title (CharField): The title of the lesson.
        content (TextField): The content of the lesson.
        total_attempt (IntegerField): The total number of attempts allowed for this lesson, not editable by users.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")  # Act as a foreign key
    title = models.CharField(null=False, max_length=200, default="title")
    content = models.TextField()
    total_attempt = models.IntegerField(default=3, editable=False)

    def __str__(self):
        return f"{self.title}"


# Enrollment model
class Enrollment(models.Model):
    """
    Represents the enrollment of a user in a course, including details such as the user, course, date of enrollment,
    mode of enrollment, and rating.
    Attributes:
        AUDIT (str): Constant for audit mode.
        HONOR (str): Constant for honor mode.
        BETA (str): Constant for beta mode.
        COURSE_MODES (list): List of tuples containing course mode choices.
        user (ForeignKey): Foreign key to the user model.
        course (ForeignKey): Foreign key to the course model.
        date_enrolled (DateField): Date when the user enrolled in the course.
        mode (CharField): Mode of enrollment, with choices defined in COURSE_MODES.
        rating (FloatField): Rating given by the user, default is 5.0.
    """

    AUDIT = "audit"
    HONOR = "honor"
    BETA = "BETA"

    COURSE_MODES = [(AUDIT, "Audit"), (HONOR, "Honor"), (BETA, "BETA")]

    # Act as a foreign key
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")

    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


class Attempt(models.Model):
    """
    Represents an attempt made by a learner on a lesson.
    Attributes:
        learner (ForeignKey): A reference to the User who made the attempt.
        lesson (ForeignKey): A reference to the Lesson being attempted.
    Methods:
        `decrease_attempt()`: Decreases the remaining attempts by 1 if there are attempts left and saves the instance.
        `has_attempts_left()`: Checks if there are any remaining attempts.
        `__str__()`: Returns a string representation of the attempt, including the username and lesson title.
    """

    # Act as foreign key
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attempts")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attempts")
    attempt_no = models.IntegerField(default=0, editable=False)
    remaining_attempts = models.IntegerField(null=True, editable=False)

    class Meta:
        unique_together = ["learner", "lesson", "attempt_no"]

    def decrease_attempt(self):
        if self.remaining_attempts > 0:
            self.remaining_attempts -= 1
            self.save()

    @classmethod
    def create_attempt(cls, learner, lesson, attempt_no, remaining_attempts=3):
        return cls.objects.create(
            learner=learner, lesson=lesson, attempt_no=attempt_no, remaining_attempts=remaining_attempts
        )

    def __str__(self):
        return f"{self.learner.username}'s attempt for {self.lesson.title}"


class Question(models.Model):
    """
    Represents a question within a course in the online course application.

    Attributes:
        lesson (ForeignKey): The lesson to which the question belongs.
        question_text (CharField): The text of the question, limited to 200 characters.
        grade (IntegerField): The grade assigned to the question, default is 100.
        expect_multiple_answer (BooleanField): Indicates if the question expects multiple answers.
    Methods:
        `is_get_score(selected_ids)`: Determines if the selected choices are correct.
    """

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=200)  # Content of the question
    grade = models.IntegerField(default=100, editable=False)
    expect_multiple_answer = models.BooleanField(default=False)

    def is_get_score(self, selected_ids) -> bool:
        """
        Determine if the selected choices are correct.

        Args:
            selected_ids (int): IDs of the selected choices retrieved from the form.

        Returns:
            bool: True if all selected choices are correct, False otherwise.
        """

        all_answers = self.choices.filter(is_correct=True).count()
        selected_correct = self.choices.filter(is_correct=True, id__in=selected_ids).count()

        if all_answers == selected_correct:
            return True
        else:
            return False

    def __str__(self):
        return f"Question: {self.question_text}"


class Choice(models.Model):
    """
    Represents a choice for a question in an online course.

    Attributes:
        question (ForeignKey): A reference to the related Question object. When the related Question is deleted,
                                this choice will also be deleted.
        choice_text (TextField): The text of the choice, with a maximum length of 200 characters.
        is_correct (BooleanField): Indicates whether this choice is the correct answer to the question. Defaults to False.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.TextField(max_length=200)
    is_correct = models.BooleanField(default=False)


class Submission(models.Model):
    """
    Represents a submission made by a user for a specific lesson attempt.

    Attributes:
        attempt (ForeignKey): A reference to the Attempt model, indicating which attempt this submission belongs to.
        lesson (ForeignKey): A reference to the Lesson model, indicating which lesson this submission is for.
        choices (ManyToManyField): A many-to-many relationship with the Choice model, representing the choices made in this submission.
        submission_date (DateTimeField): The date and time when the submission was created, automatically set to the current date and time.
    """

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="submissions")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="submissions")
    choices = models.ManyToManyField(Choice)
    submission_date = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, editable=False)
