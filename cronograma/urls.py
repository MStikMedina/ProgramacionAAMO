from django.urls import path
from .views import dashboard_cronograma, cargar_grados, obtener_materias, obtener_unidades, configurar_colegio

urlpatterns = [
    path('', dashboard_cronograma, name='dashboard'),
    path('ajax/cargar-grados/', cargar_grados, name='ajax_cargar_grados'),
    path('ajax/obtener-materias/', obtener_materias, name='ajax_obtener_materias'),
    path('ajax/obtener-unidades/', obtener_unidades, name='ajax_obtener_unidades'),
    path('configurar-colegio/<int:colegio_id>/', configurar_colegio, name='configurar_colegio'),
]