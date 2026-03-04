from django.urls import path
from .views import dashboard_colegios, cargar_grados, obtener_materias, obtener_unidades, configurar_colegio
from .exports import descargar_excel_colegio, descargar_excel_profesor

urlpatterns = [
    path('', dashboard_colegios, name='dashboard'),
    path('ajax/cargar-grados/', cargar_grados, name='ajax_cargar_grados'),
    path('ajax/obtener-materias/', obtener_materias, name='ajax_obtener_materias'),
    path('ajax/obtener-unidades/', obtener_unidades, name='ajax_obtener_unidades'),
    path('configurar-colegio/<int:colegio_id>/', configurar_colegio, name='configurar_colegio'),
    path('descargar-colegio/<int:colegio_id>/', descargar_excel_colegio, name='descargar_excel_colegio'),
    path('descargar-profesor/<int:profesor_id>/', descargar_excel_profesor, name='descargar_excel_profesor'),
]