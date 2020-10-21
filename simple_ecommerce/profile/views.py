from random import randrange

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

from shop.models import Order
from user_mgmt.models import User


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
    try:
        profile_user = User.objects.get(username=email)
    except User.DoesNotExist:
        raise Http404

    return render(request, 'profile/public.html', context={'profile_user': profile_user})


@require_GET
def high_air(request):
    return render(request, 'high_air.html')
