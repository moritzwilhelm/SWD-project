from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET


@login_required()
@require_GET
def private(request, email):
    return render(request, 'profile/private.html')


@login_required()
@require_GET
def public(request, email):
    return render(request, 'profile/public.html')
