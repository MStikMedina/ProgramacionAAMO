from django.urls import path
from .views import dashboard_cronograma, cargar_grados

urlpatterns = [
    path('', dashboard_cronograma, name='dashboard'),
    path('ajax/cargar-grados/', cargar_grados, name='ajax_cargar_grados'),
]