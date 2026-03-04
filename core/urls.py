from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('configuracion/', include('configuracion.urls')),
    path('colegios/', include('colegios.urls')),
    path('profesores/', include('profesores.urls')),
    path('general/', include('general.urls')),
]