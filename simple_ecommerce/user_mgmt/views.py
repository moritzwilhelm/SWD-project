from django.contrib import messages
from django.contrib.auth import login, password_validation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from google.auth.transport import requests
from google.oauth2 import id_token

from user_mgmt.forms import CustomUserCreationForm, PasswordResetRequestForm, CustomPasswordResetForm
from user_mgmt.models import User, PasswordResetToken


@login_required()
@require_GET
def index(request):
    return render(request, 'user_mgmt/index.html')


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        messages.success(request, 'Logout successful')
        return logout_then_login(request)
    else:
        return HttpResponse(status=401)


@require_http_methods(['GET', 'POST'])
def registration_view(request):
    if request.method == 'GET':
        return render(request, 'user_mgmt/registration.html', {'form': CustomUserCreationForm()})
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, f"Activation link sent to '{user.username}'")
            send_mail('Activation Link',
                      f"http://localhost:3000/accounts/{user.username}/verify/{user.activation_token}/",
                      'shop@speedwagon.foundation', [user.username])
            return redirect(reverse('accounts:index'))
        messages.warning(request, 'Registration failed')
        return render(request, 'user_mgmt/registration.html', {'form': form})


@require_GET
def verify(request, email, token):
    user = get_object_or_404(User, username=email, activation_token=token)
    if not user.is_active:
        user.is_active = True
        user.datetime_joined = timezone.now()
        user.save()
        messages.success(request, 'Account successfully activated')
        return redirect(reverse('accounts:index'))
    else:
        raise Http404


@require_http_methods(['GET', 'POST'])
def password_forgotten(request):
    if request.user.is_authenticated:
        raise Http404

    if request.method == 'GET':
        return render(request, 'user_mgmt/password_forgotten.html', {'form': PasswordResetRequestForm()})
    else:
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username, is_active=True)
                token, _ = PasswordResetToken.objects.get_or_create(user=user)
                token.value = get_random_string(length=16)
                token.save()
                send_mail('Password reset link',
                          f"Reset your password at http://localhost:3000/accounts/{user.username}/reset/{token.value}/",
                          'shop@speedwagon.foundation', [user.username])
            except User.DoesNotExist:
                pass

            messages.success(request, f"Password reset instructions sent to '{username}'")
        return render(request, 'user_mgmt/password_forgotten.html', {'form': form})


def _is_valid_password_reset(request, password1, password2):
    if password1 == password2:
        try:
            password_validation.validate_password(password1, request.user)
        except ValidationError as error:
            messages.warning(request, '\n'.join(error))
            return False
        return True
    else:
        messages.warning(request, 'The two password fields didn’t match.')
        return False


@require_http_methods(['GET', 'POST'])
def reset_password(request, email, token):
    user = get_object_or_404(User, username=email, is_active=True)
    token = get_object_or_404(PasswordResetToken, user=user, value=token)

    if request.method == 'GET':
        return render(request, 'user_mgmt/reset.html', {'form': CustomPasswordResetForm()})
    else:
        form = CustomPasswordResetForm(request.POST, user)
        if form.is_valid() and \
                _is_valid_password_reset(request, form.cleaned_data['password1'], form.cleaned_data['password2']):
            user.set_password(form.cleaned_data['password1'])
            user.save()
            token.delete()
            messages.success(request, f"Successfully reset password for '{user.username}'")
            return redirect(reverse('accounts:login'))

        return render(request, 'user_mgmt/reset.html', {'form': form})


@require_POST
def token_sign_in(request):
    token = request.POST.get('id_token', '')
    if not token:
        return HttpResponse(status=400)
    try:
        client_id = '39346139449-nrl3aj1sc0cijkbpg4h0prtgbmb8trs1.apps.googleusercontent.com'
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        username = idinfo['email']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=None, first_name=idinfo['given_name'],
                                            last_name=idinfo['family_name'])
            user.is_active = True
            user.datetime_joined = timezone.now()
            user.save()

        login(request, user)
        return HttpResponse(status=200)
    except ValueError:
        return HttpResponse(status=400)
