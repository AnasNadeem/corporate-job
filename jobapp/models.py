from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# from rest_framework.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from model_utils import Choices
from jobapp.models_manager import UserManager


class TimeBaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, blank=False)
    age = models.IntegerField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()


class Corporate(TimeBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=50, blank=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Job(TimeBaseModel):
    corporate = models.ForeignKey(Corporate, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    total_interest = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Profile(TimeBaseModel):
    QUALIFICATION_CHOICES = Choices(
        ('highschool', 'High School'),
        ('ug', 'Undergraduate Degree'),
        ('pg', 'Postgraduate Degree'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=250, blank=True)
    job_preference = models.CharField(max_length=250, blank=True)
    qualification = models.CharField(max_length=50, choices=QUALIFICATION_CHOICES, blank=True)
    expected_ctc = models.IntegerField(null=True, blank=True, help_text='Annualy in Lakh')
    experience = models.IntegerField(null=True, blank=True, help_text='In Years')
    earliest_possible_join_date = models.DateField(null=True, blank=True)
    job_expectations = models.CharField(max_length=250, blank=True)
    is_paid = models.BooleanField(default=False)
    interest_jobs = models.ManyToManyField(Job, blank=True)

    def __str__(self):
        return self.user.email
