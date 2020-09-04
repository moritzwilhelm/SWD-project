from django.db import models
from django.utils.translation import gettext_lazy as _

from user_mgmt.models import User


class Partner(models.Model):
    name = models.CharField(max_length=30)
    web_site = models.URLField()
    token = models.CharField(_('token'), max_length=128, unique=True)


class Product(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    slug = models.SlugField()
    price = models.FloatField()
    special_price = models.FloatField()
    count = models.IntegerField()
    image = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, default=None)
