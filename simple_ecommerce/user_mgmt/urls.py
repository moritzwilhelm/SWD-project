from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('accounts/login/', LoginView.as_view(template_name='user_mgmt/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/registration/', views.registration_view, name='registration'),
    path('accounts/<str:email>/verify/<str:token>/', views.verify, name='verify'),

    path('accounts/password-reset/', views.password_forgotten, name='password_forgotten'),
    path('accounts/<str:email>/reset/<str:token>/', views.reset_password, name='reset_password'),

    path('accounts/tokensignin/', views.token_sign_in, name='tokensignin')
]
