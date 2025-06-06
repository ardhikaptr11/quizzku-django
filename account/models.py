from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Authentication
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30)

    # Basic information
    profile_image = models.ImageField(null=True, upload_to="profile_images/", default=None)
    full_name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, null=True)
    birth_date = models.DateField(null=True)
    address = models.CharField(null=True, max_length=100, default=None)
    phone_number = models.CharField(null=True, max_length=16)
    institution = models.CharField(null=True, max_length=100, default=None)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Permissions
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_empty_fields(self):
        empty_field = []

        excluded_fields = [
            "id",
            "email",
            "username",
            "password",
            "date_joined",
            "is_staff",
            "is_superuser",
            "last_login",
        ]

        for field in self._meta.fields:
            if field.name in excluded_fields:
                continue

            field_name = field.name
            value = getattr(self, field_name)
            if value in [None, ""]:
                empty_field.append(field_name)

        learner = self.learners.get()
        if learner.social_link in [None, ""]:
            empty_field.append("social_link")

        if learner.profession in [None, ""]:
            empty_field.append("profession")

        return empty_field, excluded_fields

    def completion_percentage(self):
        empty_fields, excluded_fields = self.get_empty_fields()

        total_fields = len(self._meta.fields) - len(excluded_fields)
        total_fields += 2  # Add learner's fields (i.e. social_link and profession)

        empty_fields_count = len(empty_fields)
        filled_fields = total_fields - empty_fields_count
        completion = (filled_fields / total_fields) * 100
        return round(completion, 2)

    def __str__(self):
        return self.full_name


class Learner(models.Model):
    # Assign experience level
    IT = "information technology"
    EMP = "engineering, math, and physics"
    LNJ = "law and justice"
    HCS = "history and cultural studies"
    SPE = "sport and physical education"
    SIS = "social and international studies"
    HMB = "health, medicine, and biological sciences"
    ENS = "environmental studies and sustainability"

    FIELD_OF_INTEREST_CHOICES = [
        (IT, "Information Technology (IT)"),
        (EMP, "Engineering, Math, and Physics"),
        (LNJ, "Law and Justice"),
        (HCS, "History and Cultural Studies"),
        (SPE, "Sport and Physical Education"),
        (SIS, "Social and International Studies"),
        (HMB, "Health, Medicine, and Biological Sciences"),
        (ENS, "Environmental Studies and Sustainability"),
    ]

    # Define model fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learners")  # Act as a foreign key
    field_of_interest = models.CharField(null=True, max_length=50, choices=FIELD_OF_INTEREST_CHOICES, default=None)
    social_link = models.URLField(null=True, max_length=200, default=None)
    profession = models.CharField(null=True, max_length=50, default=None)

    def __str__(self):
        return f"{self.user.username}"


class Instructor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="instructors")  # Act as a foreign key
    work_experience = models.IntegerField()
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return f"{self.user.username}"
