from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


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
    username = models.CharField(blank=True, max_length=140, null=True)
    first_name = models.CharField(blank=True, max_length=140, null=True)
    last_name = models.CharField(blank=True, max_length=140, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = LifionUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
