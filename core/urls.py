from django.contrib import admin
from django.urls import path, include
from gestion_datos.views import gestion_libros, gestion_colegios, gestion_profesores
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('configuracion/libros/', gestion_libros, name='gestion_libros'),
    path('configuracion/colegios/', gestion_colegios, name='gestion_colegios'),
    path('configuracion/profesores/', gestion_profesores, name='gestion_profesores'),
    path('cronograma/', include('cronograma.urls')),
]
