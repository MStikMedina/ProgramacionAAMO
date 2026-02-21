from django.contrib import admin
from django.urls import path, include
from gestion_datos.views import gestion_libros, gestion_colegios, gestion_profesores

urlpatterns = [
    path('admin/', admin.site.urls),
    path('libros/', gestion_libros, name='gestion_libros'),
    path('colegios/', gestion_colegios, name='gestion_colegios'),
    path('profesores/', gestion_profesores, name='gestion_profesores'),
    path('cronograma/', include('cronograma.urls')),
]
