from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('api/products/', views.get_many, name='get_many'),
    path('api/products/<int:product_id>/', views.fetch_or_delete, name='fetch_or_delete'),
    path('api/products/create/', views.create, name='create'),

    # only for testing purposes
    path('api/register_partner/', views.register, name='register')
]
