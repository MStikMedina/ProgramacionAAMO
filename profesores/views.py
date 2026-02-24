from django.shortcuts import render
from cronograma.models import Clase, Asignacion
from gestion_datos.models import Profesor, Libro

def ver_horario(request):
    profesor_id = request.GET.get('profesor_id')
    profesores = Profesor.objects.all().order_by('nombre')
    clases_data = []

    if profesor_id:
        # Ordenamos estrictamente por fecha y luego por hora (formato 24h o numérico es mejor)
        # Aquí ordenamos por el campo bloque__hora para asegurar el orden cronológico
        clases = Clase.objects.filter(
            profesor_id=profesor_id, 
            cancelada=False, 
            es_evento=False
        ).select_related('colegio', 'bloque').order_by('fecha', 'bloque__hora')

        for c in clases:
            # Buscamos el libro asignado a este colegio y grado para obtener el Título (Material)
            # y los datos específicos de la unidad (Nombre y Link)
            asignacion = Asignacion.objects.filter(colegio=c.colegio, grado=c.bloque.grado).first()
            libro_titulo = asignacion.libro_titulo if asignacion else "Sin Libro Asignado"
            
            # Buscamos el detalle de la unidad en el inventario de Libros
            unidad_info = Libro.objects.filter(titulo=libro_titulo, unidad=c.unidad).first()
            
            clases_data.append({
                'clase': c,
                'material_nombre': libro_titulo,
                'unidad_nombre': unidad_info.nombre_unidad if unidad_info else c.unidad,
                'unidad_link': unidad_info.link_unidad if unidad_info else "#"
            })

    return render(request, 'profesores/horario.html', {
        'profesores': profesores,
        'clases_data': clases_data,
        'profesor_sel': profesor_id
    })