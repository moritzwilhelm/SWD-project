import json
from re import match
from urllib.parse import unquote

from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, Http404
from django.utils.crypto import get_random_string
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from shop.models import Partner, Product


def _get_partner(request):
    bearer_token = request.headers.get('Authorization', '')
    if match(r'Bearer [a-zA-Z0-9]{16}$', bearer_token) is None:
        raise Partner.DoesNotExist
    token = bearer_token.split()[1]

    for partner in Partner.objects.all():
        if check_password(token, partner.token):
            return partner
    else:
        raise Partner.DoesNotExist


@csrf_exempt
@never_cache
@require_GET
def get_many(request):
    try:
        partner = _get_partner(request)
    except Partner.DoesNotExist:
        return HttpResponse(status=400)

    try:
        page = int(request.GET.get('page'))
        pagination = int(request.GET.get('pagination'))
    except ValueError:
        return HttpResponse(status=400)
    except TypeError:
        results = Product.objects.filter(Q(partner=partner) | Q(partner=None, user=None))
    else:
        start = (page - 1) * pagination
        end = start + pagination
        try:
            results = Product.objects.filter(Q(partner=partner) | Q(partner=None, user=None)).order_by('id')[start:end]
        except AssertionError:
            return HttpResponse(status=400)
    return JsonResponse({'result': [model_to_dict(result) for result in results]}, json_dumps_params={'indent': 2})


@csrf_exempt
@never_cache
@require_http_methods(['GET', 'DELETE'])
def fetch_or_delete(request, product_id):
    try:
        partner = _get_partner(request)
    except Partner.DoesNotExist:
        return HttpResponse(status=400)

    product = Product.objects.filter(Q(partner=partner, id=product_id) | Q(partner=None, user=None, id=product_id))
    if not product.exists():
        raise Http404
    if request.method == 'GET':
        return JsonResponse({'result': model_to_dict(product.first())}, json_dumps_params={'indent': 2})
    else:
        product.first().delete()
        return HttpResponse(status=200)


@csrf_exempt
@require_POST
def create(request):
    try:
        partner = _get_partner(request)
    except Partner.DoesNotExist:
        return HttpResponse(status=400)

    values = json.loads(request.body)

    try:
        name = values['name']
        description = values['description']
        price = round(float(values['price']), 2)
        special_price = round(float(values['special_price']), 2)
        count = int(values['count'])
        image = unquote(values['image'])
    except (KeyError, ValueError):
        return HttpResponse(status=400)

    if price < 0.00 or special_price < 0.00 or special_price > price or count <= 0.00:
        return HttpResponse(status=400)

    slug = name.replace(' ', '-') + get_random_string(length=4)
    Product.objects.create(name=name, description=description, price=price, special_price=special_price,
                           count=count, image=image, slug=slug, partner_id=partner.id)
    return HttpResponse(status=200)


# only for testing purposes
@csrf_exempt
@never_cache
@require_POST
def register(request):
    name = request.POST.get('name', '')
    web_site = request.POST.get('web_site', '')
    if not name or not web_site:
        return HttpResponse(status=400)

    partner = Partner(name=name, web_site=web_site)
    try:
        raw_token = get_random_string(length=16)
        partner.token = make_password(raw_token)
    except IntegrityError:
        return HttpResponse(status=400, content='Something went wrong, please try again')
    partner.save()

    return HttpResponse(status=200, content=raw_token)
