from django.contrib import admin
from django.urls import path, include
from .views import home

# Handlers de error personalizados — solo activos cuando DEBUG=False
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('colegios/', include('colegios.urls')),
    path('profesores/', include('profesores.urls')),
    path('general/', include('general.urls')),
]