from django.shortcuts import render, redirect
from django.http import JsonResponse
from colegios.models import Clase, Asignacion, ClaseParticular
from configuracion.models import Profesor, Libro
from collections import defaultdict

def extraer_minutos(hora_str):
    try:
        h = hora_str.split('-')[0].strip().split(':')
        return int(h[0]) * 60 + int(h[1])
    except:
        return 0

# --- FUNCIONES AJAX PARA EL FORMULARIO ---
def obtener_asignaturas_particular(request):
    material = request.GET.get('material')
    if material:
        asignaturas = Libro.objects.filter(titulo=material).values_list('materia', flat=True).distinct()
        return JsonResponse(list(asignaturas), safe=False)
    return JsonResponse([])

def obtener_unidades_particular(request):
    material = request.GET.get('material')
    materia = request.GET.get('materia')
    if material and materia:
        unidades = Libro.objects.filter(titulo=material, materia=materia).values('unidad', 'nombre_unidad')
        return JsonResponse(list(unidades), safe=False)
    return JsonResponse([])

# --- VISTA PRINCIPAL ---
def ver_horario(request):
    # Procesar guardado, edición o eliminación de Clase Particular (Solo Admins)
    if request.method == 'POST' and request.user.is_staff:
        profesor_id = request.POST.get('profesor_id')
        
        if 'guardar_particular' in request.POST:
            ClaseParticular.objects.create(
                profesor_id=profesor_id,
                estudiante=request.POST.get('estudiante'),
                ciudad=request.POST.get('ciudad'),
                mapa_link=request.POST.get('mapa_link'),
                fecha=request.POST.get('fecha'),
                hora=request.POST.get('hora'),
                grado=request.POST.get('grado'),
                material=request.POST.get('material'),
                materia=request.POST.get('materia'),
                unidad=request.POST.get('unidad')
            )
        elif 'editar_particular' in request.POST:
            p_id = request.POST.get('particular_id')
            ClaseParticular.objects.filter(id=p_id).update(
                estudiante=request.POST.get('estudiante'),
                ciudad=request.POST.get('ciudad'),
                mapa_link=request.POST.get('mapa_link'),
                fecha=request.POST.get('fecha'),
                hora=request.POST.get('hora'),
                grado=request.POST.get('grado'),
                material=request.POST.get('material'),
                materia=request.POST.get('materia'),
                unidad=request.POST.get('unidad')
            )
        elif 'eliminar_particular' in request.POST:
            p_id = request.POST.get('particular_id')
            ClaseParticular.objects.filter(id=p_id).delete()
            
        return redirect(f"{request.path}?profesor_id={profesor_id}")

    profesor_id = request.GET.get('profesor_id')
    profesores = Profesor.objects.all().order_by('nombre')
    agrupado_por_fecha = []
    
    # Extraer todos los títulos de libros únicos para el primer selector
    todos_libros = Libro.objects.values_list('titulo', flat=True).distinct()

    if profesor_id:
        temp_dict = defaultdict(list)
        
        # 1. Cargar Clases Normales
        clases = Clase.objects.filter(
            profesor_id=profesor_id, 
            cancelada=False, 
            es_evento=False
        ).select_related('colegio', 'bloque').order_by('fecha')

        for c in clases:
            asig = Asignacion.objects.filter(colegio=c.colegio, grado=c.bloque.grado).first()
            libro_titulo = asig.libro_titulo if asig else "Sin Libro"
            unidad_obj = Libro.objects.filter(titulo=libro_titulo, materia=c.materia, unidad=c.unidad).first()

            temp_dict[c.fecha].append({
                'clase': c,
                'minutos': extraer_minutos(c.bloque.hora),
                'material': libro_titulo,
                'unidad_full': f"{c.unidad}. {unidad_obj.nombre_unidad}" if unidad_obj else c.unidad,
                'unidad_link': unidad_obj.link_unidad if unidad_obj else "#",
                'maps_link': getattr(c.colegio, 'mapa_link', '#') or '#',
                'es_particular': False # Bandera para el HTML
            })

        # 2. Cargar Clases Particulares
        particulares = ClaseParticular.objects.filter(profesor_id=profesor_id).order_by('fecha')
        
        for p in particulares:
            unidad_obj = Libro.objects.filter(titulo=p.material, materia=p.materia, unidad=p.unidad).first()
            
            falsa_clase = {
                'colegio': {'nombre': f"{p.estudiante} (Part.)", 'ciudad': p.ciudad},
                'bloque': {'hora': p.hora, 'grado': p.grado},
                'materia': p.materia
            }

            temp_dict[p.fecha].append({
                'clase': falsa_clase,
                'minutos': extraer_minutos(p.hora),
                'material': p.material,
                'unidad_full': f"{p.unidad}. {unidad_obj.nombre_unidad}" if unidad_obj else p.unidad,
                'unidad_link': unidad_obj.link_unidad if unidad_obj else "#",
                'maps_link': p.mapa_link or '#',
                'es_particular': True, # Bandera para el HTML
                'particular_id': p.id,
                'raw_data': { # Datos puros para inyectar en el Modal de Edición
                    'estudiante': p.estudiante, 'ciudad': p.ciudad, 
                    'fecha': p.fecha.strftime('%Y-%m-%d'), 'hora': p.hora, 
                    'grado': p.grado, 'materia': p.materia, 'unidad': p.unidad
                }
            })

        # 3. Ordenar todo por fecha y luego por hora
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
        'profesor_sel': profesor_id,
        'todos_libros': todos_libros
    })