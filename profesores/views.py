from django.shortcuts import render
from colegios.models import Clase, Asignacion
from configuracion.models import Profesor, Libro
from collections import defaultdict

def extraer_minutos(hora_str):
    try:
        h = hora_str.split('-')[0].strip().split(':')
        return int(h[0]) * 60 + int(h[1])
    except:
        return 0

def ver_horario(request):
    profesor_id = request.GET.get('profesor_id')
    profesores = Profesor.objects.all().order_by('nombre')
    agrupado_por_fecha = []

    if profesor_id:
        clases = Clase.objects.filter(
            profesor_id=profesor_id, 
            cancelada=False, 
            es_evento=False
        ).select_related('colegio', 'bloque').order_by('fecha')

        temp_dict = defaultdict(list)
        for c in clases:
            asig = Asignacion.objects.filter(colegio=c.colegio, grado=c.bloque.grado).first()
            libro_titulo = asig.libro_titulo if asig else "Sin Libro"
            
            unidad_obj = Libro.objects.filter(
                titulo=libro_titulo, 
                materia=c.materia, 
                unidad=c.unidad
            ).first()

            temp_dict[c.fecha].append({
                'clase': c,
                'minutos': extraer_minutos(c.bloque.hora),
                'material': libro_titulo,
                'unidad_full': f"{c.unidad}. {unidad_obj.nombre_unidad}" if unidad_obj else c.unidad,
                'unidad_link': unidad_obj.link_unidad if unidad_obj else "#",
                'maps_link': getattr(c.colegio, 'mapa_link', '#') or '#'
            })

        for fecha in sorted(temp_dict.keys()):
            clases_ordenadas = sorted(temp_dict[fecha], key=lambda x: x['minutos'])
            agrupado_por_fecha.append({
                'fecha': fecha,
                'cantidad': len(clases_ordenadas),
                'clases': clases_ordenadas
            })

    return render(request, 'profesores/horario.html', {
        'profesores': profesores,
        'agrupado': agrupado_por_fecha,
        'profesor_sel': profesor_id
    })