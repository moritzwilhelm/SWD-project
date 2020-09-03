from django.urls import path

from . import views

app_name = 'profile'

urlpatterns = [
    path('profile/<str:email>/private/', views.private, name='private'),
    path('profile/<str:email>/public-store/', views.public, name='public')
]