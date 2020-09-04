import json
from re import match
from urllib.parse import unquote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from shop.models import Partner, Product, Order, CartItem, Address, Payment


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


@login_required()
@require_GET
def list_products(request):
    return render(request, 'shop/shop.html', context={'products': Product.objects.all()})


@login_required()
@require_GET
def get_product(request, product_id):
    product = Product.objects.filter(id=product_id).values('id', 'name', 'slug', 'description', 'price', 'count')
    if product.exists:
        return JsonResponse(product.first(), json_dumps_params={'indent': 2})
    else:
        raise Http404


@login_required()
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    if product_id is None:
        return HttpResponse(status=400, reason='Missing parameters')

    try:
        product = Product.objects.get(id=product_id, count__gt=0)
    except Product.DoesNotExist:
        messages.warning(request, 'This product is currently out of stock')
    else:
        order, _ = Order.objects.get_or_create(customer_id=request.user, placed=False)
        cart_item, _ = CartItem.objects.get_or_create(product_id=product, order_id=order)
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Successfully added {product.name} to basket")
    return redirect(reverse('shop:list_products'))


@login_required()
@require_GET
def show_basket(request, order_id=None):
    if order_id is None:
        order, _ = Order.objects.get_or_create(customer_id=request.user, placed=False)
        return redirect(reverse('shop:show_basket', kwargs={'order_id': order.id}))

    try:
        order = Order.objects.get(id=order_id, customer_id=request.user)
    except Order.DoesNotExist:
        return HttpResponse(status=403)

    price = sum(
        [cart_item.product_id.price for cart_item in order.cartitem_set.iterator() for i in range(cart_item.quantity)])
    return render(request, 'shop/basket.html',
                  context={'order': order,
                           'price': price})


@login_required()
@require_POST
def delete_from_basket(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, order_id__placed=False)
    except CartItem.DoesNotExist:
        raise Http404

    cart_item.quantity -= 1
    cart_item.save()

    if cart_item.quantity == 0:
        cart_item.delete()

    messages.success(request, f"Successfully removed 1x '{cart_item.product_id.name}' from your basket")

    return redirect(reverse('shop:show_current_basket'))


@login_required()
@require_http_methods(['GET', 'POST'])
def checkout(request, order_id):
    try:
        order = Order.objects.get(id=order_id, customer_id=request.user, placed=False)
    except Order.DoesNotExist:
        return HttpResponse(status=403)

    if request.method == 'GET':
        return render(request, 'shop/checkout.html', context={'order': order})
    else:
        for item in order.cartitem_set.iterator():
            if item.quantity > item.product_id.count:
                messages.warning(request, f'The requested quantity of {item.product_id.name} exceeds '
                                          f'the currently available stock of {item.product_id.count}')
                return redirect(reverse('shop:show_current_basket'))

        street = request.POST.get('street', '')
        city = request.POST.get('city', '')
        zip_code = request.POST.get('zip_code', '')
        country = request.POST.get('country', '')
        info = request.POST.get('additional_info', '')
        method = request.POST.get('method', '')

        if not (street and city and zip_code and country and method and order.cartitem_set):
            return HttpResponse(status=400, reason='Missing Parameters')

        if method not in ['PayPal', 'Credit Card', 'Cash', 'Red stone of Aya']:
            return HttpResponse(status=400, reason='Illegal payment method')

        try:
            address, _ = Address.objects.get_or_create(street=street, city=city, zip_code=zip_code, country=country,
                                                       additional_info=info)
        except ValueError:
            return HttpResponse(400)

        amount = sum([cart_item.product_id.price for cart_item in order.cartitem_set.iterator() for i in
                      range(cart_item.quantity)])
        payment, _ = Payment.objects.get_or_create(method=method, amount=amount)

        order.shipping_address = address
        order.payment = payment
        order.date_placed = timezone.now().date()

        for cart_item in order.cartitem_set.iterator():
            cart_item.product_id.count -= cart_item.quantity
            cart_item.product_id.save()

        order.placed = True
        order.save()
        messages.success(request, 'Order successful')
        return redirect(reverse('shop:list_products'))
