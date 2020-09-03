from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from shop.models import Order


@login_required()
@require_GET
def private(request, email):
    if request.user.username == email:
        orders = Order.objects.filter(customer_id=request.user, placed=True).order_by("-date_placed", "-id")
        return render(request, 'profile/private.html', context={'orders': orders})
    else:
        return HttpResponse()


@login_required()
@require_GET
def public(request, email):
    return render(request, 'profile/public.html')
