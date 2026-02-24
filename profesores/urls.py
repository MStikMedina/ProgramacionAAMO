from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_horario, name='ver_horario'),
]