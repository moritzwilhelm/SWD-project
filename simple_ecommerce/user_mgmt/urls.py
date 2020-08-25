from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/registration/', views.registration_view, name='registration'),
    path('accounts/<str:email>/verify/<str:token>/', views.verify, name='verify'),
]
