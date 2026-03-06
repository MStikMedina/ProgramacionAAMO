from django.urls import path
from . import views

urlpatterns = [
    path('login/',    views.vista_login,        name='login'),
    path('logout/',   views.vista_logout,        name='logout'),
    path('gestionar/', views.gestionar_usuarios, name='gestionar_usuarios'),
]