from django.contrib import admin

# Register your models here.
from .models import Instructor, Learner

admin.site.register(Instructor)
admin.site.register(Learner)