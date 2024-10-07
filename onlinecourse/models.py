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

from django.utils.timezone import now

# Errror handling if Django module is missing or not installed
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings

# Define the models for the online course application


# Instructor model
class Instructor(models.Model):
    """
    A model representing an instructor in the online course application.

    The Instructor model includes the following fields:

        user (ForeignKey): A reference to the user associated with the instructor.
        full_time (BooleanField): A boolean indicating whether the instructor is full-time. Defaults to True.
        total_learners (IntegerField): An integer representing the total number of learners taught by the instructor.

    Methods:

        __str__: Returns the username of the associated user as the string representation of the Instructor instance.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Act as a foreign key
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    """
    A model representing a learner in the online course application.

    Attributes:
        STUDENT (str): Constant for student occupation.
        DEVELOPER (str): Constant for developer occupation.
        DATA_SCIENTIST (str): Constant for data scientist occupation.
        DATABASE_ADMIN (str): Constant for database admin occupation.
        OCCUPATION_CHOICES (list): List of tuples containing occupation choices.
        user (ForeignKey): A reference to the user associated with the learner.
        occupation (CharField): The occupation of the learner, with choices defined in OCCUPATION_CHOICES.
        social_link (URLField) : A URL to the learner's social profile.
    """

    # Assign occupation
    STUDENT = "student"
    DEVELOPER = "developer"
    DATA_SCIENTIST = "data_scientist"
    DATABASE_ADMIN = "dba"

    # Define occupation choices
    OCCUPATION_CHOICES = [
        (STUDENT, "Student"),
        (DEVELOPER, "Developer"),
        (DATA_SCIENTIST, "Data Scientist"),
        (DATABASE_ADMIN, "Database Admin"),
    ]

    # Define model fields
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Act as a foreign key
    occupation = models.CharField(null=False, max_length=20, choices=OCCUPATION_CHOICES, default=STUDENT)
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + self.occupation


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
    image = models.ImageField(upload_to="course_images/")
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    total_enrollment = models.IntegerField(default=0)
    # Define model relationships
    # Model has a many-to-many relationship with Instructor
    instructors = models.ManyToManyField(Instructor)
    # Model has a many-to-many relationship with User through Enrollment
    # In other words, it's not a direct relationship
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Enrollment")

    def __str__(self):
        return "Name: " + self.name + "," + "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    """
    Represents a lesson in the online course application.

    Attributes:
        title (CharField): The title of the lesson with a maximum length of 200 characters. Defaults to "title".
        order (IntegerField): The order of the lesson within the course. Defaults to 0.
        course (ForeignKey): A foreign key relationship to the Course model. Deletes the lesson if the course is deleted.
        content (TextField): The content of the lesson.
    """

    title = models.CharField(null=False, max_length=200, default="title")
    order = models.IntegerField(default=0)
    content = models.TextField()
    attempt = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Act as a foreign key


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


class Question(models.Model):
    """
    Represents a question within a course in the online course application.

    Attributes:
        course (ForeignKey): The course to which the question belongs.
        lesson (ForeignKey): The lesson to which the question belongs.
        question_text (CharField): The text of the question, limited to 200 characters.
        grade (IntegerField): The grade assigned to the question, default is 50.

    `Methods`:
        is_get_score(selected_ids): Determines if the selected choices are correct.
    """

    def is_get_score(self, selected_ids) -> bool:
        """
        Determine if the selected choices are correct.

        Args:
            selected_ids (int): IDs of the selected choices retrieved from the form.

        Returns:
            bool: True if all selected choices are correct, False otherwise.
        """

        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()

        if all_answers == selected_correct:
            return True
        else:
            return False

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)  # Content of the question
    grade = models.IntegerField(default=100)
    expect_multiple_answer = models.BooleanField(default=False)

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

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.TextField(max_length=200)
    is_correct = models.BooleanField(default=False)


class Submission(models.Model):
    """
    Represents a submission made by a student for a particular lesson in the online course.
    Attributes:
        lesson (ForeignKey): A reference to the Lesson model, indicating the lesson for which
                                this submission is made.
        choices (ManyToManyField): A many-to-many relationship with the Choice model, representing
                                    the choices selected by the student in this submission.
    """

    # enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
