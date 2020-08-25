from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from user_mgmt.forms import CustomUserCreationForm


@require_GET
def index(request):
    if request.user.is_authenticated:
        return HttpResponse("Well done")
    else:
        return render(request, 'user_mgmt/registration.html', {'form': CustomUserCreationForm()})


def login_view(request):
    return None


def logout_view(request):
    return None


@require_POST
def registration_view(request):
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
    return redirect(reverse('accounts:index'))


def verify(request):
    return None
