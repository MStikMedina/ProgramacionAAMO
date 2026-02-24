from django.urls import path
from . import views

urlpatterns = [
    path('horario/', views.ver_horario, name='ver_horario'),
]