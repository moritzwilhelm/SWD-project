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


class Payment(models.Model):
    amount = models.FloatField()
    method = models.CharField(max_length=30)


class Address(models.Model):
    user = models.ManyToManyField(User)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    zip_code = models.IntegerField()
    country = models.CharField(max_length=200)
    additional_info = models.CharField(max_length=200)


class Order(models.Model):
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    placed = models.BooleanField(default=False)
    date_placed = models.DateTimeField(null=True)
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True)


class CartItem(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)

    @property
    def total_cost(self):
        return self.quantity * self.product_id.price
