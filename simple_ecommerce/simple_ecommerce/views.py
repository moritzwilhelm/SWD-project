from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET


@require_GET
def index(request):
    return redirect(reverse('accounts:index'))
