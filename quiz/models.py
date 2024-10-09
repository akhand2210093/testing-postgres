from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
#commit

from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, student_number, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not student_number:
            raise ValueError('Users must have a student number')

        user = self.model(
            email=self.normalize_email(email),
            student_number=student_number,
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_number, email, name, password):
        user = self.create_user(
            student_number=student_number,
            email=email,
            name=name,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True  # Make sure the superuser is active
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    student_number = models.CharField(max_length=9, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'student_number'
    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self):
        return f'{self.name} ({self.student_number})'

    def clean(self):
        super().clean()
        if not self.email.endswith('@akgec.ac.in'):
            raise ValidationError(_('Email must be in the domain @akgec.ac.in'))

class Question(models.Model):
    section = models.IntegerField()
    text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)  # Store only the correct answer

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)  # Store the user's answer directly

    def __str__(self):
        return f'{self.user.name} - {self.question.text}: {self.answer_text}'


class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.name}: {self.score}'
