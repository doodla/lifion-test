from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import CASCADE


class Organization(models.Model):
    name = models.CharField(max_length=30, default='')

    def __str__(self):
        return self.name


class LifionUserManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(username=username,
                                first_name=first_name,
                                last_name=last_name
                                )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class LifionUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=140, unique=True)
    first_name = models.CharField(blank=True, max_length=140, null=True)
    last_name = models.CharField(blank=True, max_length=140, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, on_delete=CASCADE, related_name='employees')

    objects = LifionUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def full_name(self):
        return self.get_full_name()

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):  # __unicode__ on Python 2
        return self.username

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"


class QuestionBank(models.Model):
    organization = models.OneToOneField(Organization, related_name='question_bank', on_delete=CASCADE)

    class Meta:
        db_table = "question_bank"
        verbose_name = "Question Bank"
        verbose_name_plural = "Question Banks"


class Question(models.Model):
    text = models.CharField(max_length=300, default='')
    bank = models.ForeignKey(QuestionBank, related_name='questions', blank=True, null=True)

    class Meta:
        db_table = "question"
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class Option(models.Model):
    text = models.CharField(max_length=100, default='')
    value = models.IntegerField(default=1)
    question = models.ForeignKey(Question, related_name='options', on_delete=CASCADE)

    class Meta:
        db_table = "option"


class Survey(models.Model):
    user = models.ForeignKey(LifionUser, related_name='surveys', on_delete=CASCADE)
    organization = models.ForeignKey(Organization, related_name='surveys', on_delete=CASCADE)
    submitters = models.ManyToManyField(LifionUser, related_name='requested_surveys')
    questions = models.ManyToManyField(Question, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    class Meta:
        db_table = "survey"


class Submission(models.Model):
    survey = models.ForeignKey(Survey, on_delete=CASCADE, related_name='submissions')
    user = models.ForeignKey(LifionUser, on_delete=CASCADE, blank=True, null=True)
    comment = models.TextField(default='')
    score = models.IntegerField(default=0)
    avg = models.DecimalField(default=0.0, max_digits=3, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField(default=False)

    @property
    def by(self):

        if self.anonymous:
            return 'Anonymous'
        else:
            return self.user.full_name

    class Meta:
        db_table = "submission"


class QuestionResponse(models.Model):
    option = models.ForeignKey(Option, on_delete=CASCADE)
    question = models.ForeignKey(Question, on_delete=CASCADE)
    submission = models.ForeignKey(Submission, related_name='responses', on_delete=CASCADE)

    class Meta:
        db_table = "question_response"
