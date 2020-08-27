from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from user_mgmt.forms import CustomUserCreationForm
from user_mgmt.models import User


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
            # print registration link
            messages.success(request,
                             f"Registration sucessful!\n"
                             f"Activate your account at: /accounts/{user.username}/verify/{user.activation_token}/")
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
