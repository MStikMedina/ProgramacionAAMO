from django.contrib import admin
from django.urls import path, include
from configuracion.views import configuracion_libros, configuracion_colegios, configuracion_profesores
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('configuracion/libros/', configuracion_libros, name='configuracion_libros'),
    path('configuracion/colegios/', configuracion_colegios, name='configuracion_colegios'),
    path('configuracion/profesores/', configuracion_profesores, name='configuracion_profesores'),
    path('colegios/', include('colegios.urls')),
    path('profesores/', include('profesores.urls')),
    path('general/', include('general.urls')),
]
