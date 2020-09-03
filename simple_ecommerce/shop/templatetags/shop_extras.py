from random import choice

from django import template

from simple_ecommerce.settings import STATIC_URL

register = template.Library()

images = ['kars.png', 'wamoo.png', 'esidesi.png', 'santana.png']


@register.simple_tag
def pillar_man():
    return f'{STATIC_URL}shop/img/{choice(images)}'
