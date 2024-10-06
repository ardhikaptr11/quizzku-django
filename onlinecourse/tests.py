from django.test import TestCase

course = get_object_or_404(Course, pk=course_id)
submission = get_object_or_404(Submission, pk=submission_id)
lesson = Lesson.objects.filter(course=course)