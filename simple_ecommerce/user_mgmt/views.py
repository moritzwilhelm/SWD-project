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

from user_mgmt.forms import CustomUserCreationForm, PasswordResetRequestForm, CustomPasswordResetForm
from user_mgmt.models import User, OneTimePassword


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
    if request.method == 'GET':
        return render(request, 'user_mgmt/passwort_forgotten.html', {'form': PasswordResetRequestForm()})
    else:
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                otp, _ = OneTimePassword.objects.get_or_create(user=user)
                otp.password = get_random_string(length=16)
                otp.save()
            except User.DoesNotExist:
                pass
            else:
                send_mail('One time password',
                          f"Reset your password at http://localhost:3000/accounts/reset/ using the OTP: {otp.password}",
                          'shop@speedwagon.foundation', [user.username])

            messages.success(request, f"Passwort reset instructions sent to '{username}'")
        return render(request, 'user_mgmt/passwort_forgotten.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def otp_verification(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            return render(request, 'user_mgmt/otp.html')
    else:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(username=username)
            otp = OneTimePassword.objects.get(user=user, password=password)
            login(request, user)
            otp.delete()
            messages.success(request, f"Successfully authenticated as '{user.username}'")
            return render(request, 'user_mgmt/reset.html', {'form': CustomPasswordResetForm()})
        except (User.DoesNotExist, OneTimePassword.DoesNotExist):
            messages.warning(request, 'Invalid credentials')
            return redirect(reverse('accounts:otp'))


def _is_valid_password_reset(request, password1, password2):
    if password1 == password2:
        try:
            password_validation.validate_password(password1, request.user)
        except ValidationError as error:
            messages.warning(request, '\n'.join(error))
            return False
        return True
    else:
        return False


@login_required()
@require_POST
def reset_password(request):
    if request.user.is_authenticated:
        form = CustomPasswordResetForm(request.POST, request.user)
        if not form.is_valid():
            messages.warning(request, 'The two password fields didn’t match.')
        elif _is_valid_password_reset(request, form.cleaned_data['password1'], form.cleaned_data['password2']):
            request.user.set_password(form.cleaned_data['password1'])
            request.user.save()
            messages.success(request, f"Successfully reset password for '{request.user.username}'")
            return redirect(reverse('accounts:login'))

        return render(request, 'user_mgmt/reset.html', {'form': form})
    else:
        return HttpResponse(status=403)
