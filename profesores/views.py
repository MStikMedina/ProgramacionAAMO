from django.shortcuts import render
from cronograma.models import Clase
from gestion_datos.models import Profesor

def ver_horario(request):
    profesor_id = request.GET.get('profesor_id')
    profesores = Profesor.objects.all().order_by('nombre')
    clases = []

    if profesor_id:
        # Filtramos: Solo clases de este profesor que NO estén canceladas ni sean eventos
        clases = Clase.objects.filter(
            profesor_id=profesor_id, 
            cancelada=False, 
            es_evento=False
        ).order_by('fecha', 'bloque__hora')

    return render(request, 'profesores/horario.html', {
        'profesores': profesores,
        'clases': clases,
        'profesor_sel': profesor_id
    })