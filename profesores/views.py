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

def _resolver_unidad(unidad, unidad_obj):
    """
    Devuelve (material_label, unidad_label, unidad_link) según el valor de la unidad.
    - A → material: 'Material Asignado'  | unidad: 'Banco de Preguntas'
    - S → material: 'Socialización de Simulacro' | unidad: 'Socialización de Simulacro'
    - N → material: título del libro | unidad: 'N. Nombre unidad'
    """
    if str(unidad) == 'A':
        return 'Material Asignado', 'Banco de Preguntas', '#'
    elif str(unidad) == 'S':
        return 'Socialización de Simulacro', 'Socialización de Simulacro', '#'
    else:
        unidad_full = f"{unidad}. {unidad_obj.nombre_unidad}" if unidad_obj else str(unidad)
        unidad_link = unidad_obj.link_unidad if unidad_obj else '#'
        return None, unidad_full, unidad_link

def ver_horario(request):
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
            ClaseParticular.objects.filter(id=request.POST.get('particular_id')).delete()
        return redirect(f"{request.path}?profesor_id={profesor_id}")

    profesor_id = request.GET.get('profesor_id')
    profesores = Profesor.objects.all().order_by('nombre')
    agrupado_por_fecha = []
    todos_libros = Libro.objects.values_list('titulo', flat=True).distinct()

    if profesor_id:
        temp_dict = defaultdict(list)

        # 1. Clases normales de colegios
        clases = Clase.objects.filter(
            profesor_id=profesor_id,
            cancelada=False,
            es_evento=False
        ).select_related('colegio', 'bloque').order_by('fecha')

        for c in clases:
            asig = Asignacion.objects.filter(
                colegio=c.colegio, grado=c.bloque.grado
            ).first()
            libro_titulo = asig.libro_titulo if asig else "Sin Libro"

            unidad_obj = Libro.objects.filter(
                titulo=libro_titulo, materia=c.materia, unidad=c.unidad
            ).first()

            material_override, unidad_full, unidad_link = _resolver_unidad(c.unidad, unidad_obj)

            temp_dict[c.fecha].append({
                'clase': c,
                'minutos': extraer_minutos(c.bloque.hora),
                # Si hay override de material (A o S), lo usamos; si no, el título del libro
                'material': material_override if material_override else libro_titulo,
                'unidad_full': unidad_full,
                'unidad_link': unidad_link,
                'maps_link': getattr(c.colegio, 'mapa_link', '#') or '#',
                'es_particular': False,
            })

        # 2. Clases particulares
        particulares = ClaseParticular.objects.filter(
            profesor_id=profesor_id
        ).order_by('fecha')

        for p in particulares:
            unidad_obj = Libro.objects.filter(
                titulo=p.material, materia=p.materia, unidad=p.unidad
            ).first()

            material_override, unidad_full, unidad_link = _resolver_unidad(p.unidad, unidad_obj)

            falsa_clase = {
                'colegio': {'nombre': f"{p.estudiante} (Part.)", 'ciudad': p.ciudad},
                'bloque': {'hora': p.hora, 'grado': p.grado},
                'materia': p.materia
            }

            temp_dict[p.fecha].append({
                'clase': falsa_clase,
                'minutos': extraer_minutos(p.hora),
                'material': material_override if material_override else p.material,
                'unidad_full': unidad_full,
                'unidad_link': unidad_link,
                'maps_link': p.mapa_link or '#',
                'es_particular': True,
                'particular_id': p.id,
                'raw_data': {
                    'estudiante': p.estudiante, 'ciudad': p.ciudad,
                    'fecha': p.fecha.strftime('%Y-%m-%d'), 'hora': p.hora,
                    'grado': p.grado, 'materia': p.materia, 'unidad': p.unidad
                }
            })

        # 3. Ordenar por fecha y hora
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