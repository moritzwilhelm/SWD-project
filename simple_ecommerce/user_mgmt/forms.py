from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string

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
