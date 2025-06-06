"""
This module configures the Django admin interface for the online course application by registering models and
defining custom admin classes.
Classes:
    QuestionInline (admin.StackedInline): Inline admin class for managing Question model instances within the
    Course admin interface.
    ChoiceInline (admin.StackedInline): Inline admin class for managing Choice model instances within the
    Question admin interface.
    LessonInline (admin.StackedInline): Inline admin class for managing Lesson model instances within the
    Course admin interface.
    CourseAdmin (admin.ModelAdmin): Custom admin class for the Course model, including inline management of
    Lesson instances and additional configurations for list display, filtering, and search fields.
    LessonAdmin (admin.ModelAdmin): Custom admin class for the Lesson model with configurations for list display.
    QuestionAdmin (admin.ModelAdmin): Custom admin class for the Question model, including inline management of
    Choice instances and configurations for list display.
Functions:
    admin.site.register: Registers the models and their corresponding admin classes with the Django admin site.
"""

from django.contrib import admin

# Import models
from .models import Choice, Course, Enrollment, Lesson, Question, Submission, Attempt

# Admin inline classes
class QuestionInline(admin.StackedInline):
    """
    QuestionInline is a Django admin inline class that allows the Question model to be edited inline within the
    admin interface. This class uses a stacked layout for displaying the inline form fields.

    Attributes:

        model (Model): The model that this inline class is associated with, which is the Question model.

        extra (int): The number of extra empty forms to display in the admin interface for adding new
        instances of the Question model.
    """

    model = Question
    extra = 2


class ChoiceInline(admin.StackedInline):
    """
    ChoiceInline is a Django admin inline class that allows the Choice model to be edited inline within the
    admin interface. This class uses a stacked layout for displaying the inline form fields.

    Attributes:

        model (Model): The model that this inline class is associated with, which is the Choice model.

        extra (int): The number of extra empty forms to display in the admin interface for adding new
        instances of the Choice model.
    """

    model = Choice
    extra = 2


class LessonInline(admin.StackedInline):
    """
    LessonInline is a Django admin inline class that allows the Lesson model to be edited inline within the admin
    interface. This class uses a stacked layout for displaying the inline form fields.

    Attributes:

        model (Model): The model that this inline class is associated with, which is the Lesson model.

        extra (int): The number of extra empty forms to display in the admin interface for adding new
        instances of the Lesson model.
    """

    model = Lesson
    extra = 5


# Custom admin classes
class CourseAdmin(admin.ModelAdmin):
    """
    CourseAdmin is a custom admin class for the Course model in the Django admin interface.

    Attributes:
        inlines (list): A list of inline models to be displayed within the Course admin interface.
        list_display (list): A list of fields to be displayed in the list view of the Course admin interface.
        list_filter (list): A list of fields to filter the Course list view.
        search_fields (list): A list of fields to be searched in the Course admin interface.
    """

    inlines = [LessonInline]
    list_display = ["name", "pub_date"]
    list_filter = ["pub_date"]
    search_fields = ["name", "description"]


class LessonAdmin(admin.ModelAdmin):
    """
    LessonAdmin is a custom admin class for the Lesson model in the Django admin interface.
    Attributes:
        list_display (list): Specifies the fields to be displayed in the list view of the admin interface.
    """

    list_display = ["title"]


class QuestionAdmin(admin.ModelAdmin):
    """
    QuestionAdmin is a custom admin class for the Question model in the Django admin interface.
    Attributes:
        inlines (list): A list of inline models to be displayed within the Question admin interface.
        list_display (list): A list of fields to be displayed in the list view of the Question admin interface.
    """

    inlines = [ChoiceInline]
    list_display = ["question_text"]


# Register models with custom admin classes
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)

# Register other models
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Enrollment)
admin.site.register(Attempt)
