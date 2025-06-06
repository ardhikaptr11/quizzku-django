from django.core.management.base import BaseCommand
from onlinecourse.models import Submission
from onlinecourse.views import calculate_grade


class Command(BaseCommand):
    help = "Backfill grades for all submissions"

    def handle(self, *args, **kwargs):
        submissions = Submission.objects.all()
        for submission in submissions:
            choices = submission.choices.all()
            questions = submission.lesson.questions.all()  

            submission.grade, _ = calculate_grade(questions=questions, choices=choices)
            submission.save(update_fields=["grade"])

        self.stdout.write(self.style.SUCCESS("Backfill completed."))
