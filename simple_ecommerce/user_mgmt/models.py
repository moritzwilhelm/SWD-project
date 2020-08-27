from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, CharField, DateTimeField
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)

        if not username:
            raise ValueError(_('username must be set'))
        username = self.normalize_email(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.datetime_joined = timezone.now()
        user.activation_token = get_random_string(length=16)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    username = EmailField(_('username'), unique=True,
                          error_messages={'unique': _("A user with that username already exists.")})
    email = None

    date_joined = None

    datetime_joined = DateTimeField(_('date joined'), blank=True, null=True)

    activation_token = CharField(_('first name'), max_length=16, blank=True)

    @property
    def enabled(self):
        return self.is_active

    objects = UserManager()
