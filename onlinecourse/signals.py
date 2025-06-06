import logging

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import Submission
from .views import calculate_grade

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Submission)
def update_submission_grade(sender, instance, created, **kwargs):
    if created and instance.lesson:
        logger.info("Submission created with ID: %s. Calculating initial grade.", instance.id)

        questions = instance.lesson.questions.all()
        choices = instance.choices.all()

        instance.grade, _ = calculate_grade(questions=questions, choices=choices)
        instance.save(update_fields=["grade"])


@receiver(m2m_changed, sender=Submission.choices.through)
def calculate_grade_on_choices_change(sender, instance, action, **kwargs):
    lesson = instance.lesson
    questions = lesson.questions.all()
    choices = instance.choices.all()

    logger.info("Calculating grade for Submission ID: %s on action: %s", instance.id, action)

    instance.grade, _ = calculate_grade(questions=questions, choices=choices)
    instance.save(update_fields=["grade"])
