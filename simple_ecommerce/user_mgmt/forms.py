from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField, Form, PasswordInput, CharField
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from user_mgmt.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user.activation_token = get_random_string(length=16)

        if commit:
            user.save()

        return user


class PasswordResetRequestForm(Form):
    username = EmailField(max_length=254)


class CustomPasswordResetForm(Form):
    password1 = CharField(label=_("Password"), max_length=32, widget=PasswordInput)
    password2 = CharField(label=_("Password confirmation"), max_length=32, widget=PasswordInput,
                          help_text='Enter the same password as before, for verification.')
