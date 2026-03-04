from django.urls import path
from .views import configuracion_libros, configuracion_colegios, configuracion_profesores

urlpatterns = [
    path('libros/', configuracion_libros, name='configuracion_libros'),
    path('colegios/', configuracion_colegios, name='configuracion_colegios'),
    path('profesores/', configuracion_profesores, name='configuracion_profesores'),
]