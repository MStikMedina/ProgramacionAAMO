from django.shortcuts import render
from django.http import JsonResponse
from .models import Bloque

# Vista temporal del dashboard (la haremos completa en el siguiente paso)
def dashboard_cronograma(request):
    return render(request, 'cronograma/dashboard.html', {})

# Función AJAX para el panel de administración
def cargar_grados(request):
    colegio_id = request.GET.get('colegio_id')
    if colegio_id:
        grados = Bloque.objects.filter(colegio_id=colegio_id).values_list('grado', flat=True).distinct()
        return JsonResponse(list(grados), safe=False)
    return JsonResponse([], safe=False)