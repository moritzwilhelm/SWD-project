from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('api/products/', views.get_many, name='get_many'),
    path('api/products/<int:product_id>/', views.fetch_or_delete, name='fetch_or_delete'),
    path('api/products/create/', views.create, name='create'),

    # only for testing purposes
    path('api/register_partner/', views.register, name='register'),

    path('shop/products/list/', views.list_products, name='list_products'),
    path('shop/products/<int:product_id>/', views.get_product, name='get_product'),
    path('shop/basket/add/', views.add_to_cart, name='add_to_cart'),
    path('shop/basket/', views.show_basket, name='show_current_basket'),
    path('shop/basket/<int:order_id>/', views.show_basket, name='show_basket'),
    path('shop/basket/delete/<int:cart_item_id>/', views.delete_from_basket, name='delete_from_basket'),
    path('shop/checkout/<int:order_id>/', views.checkout, name='checkout'),

]
