from django.shortcuts import render, redirect
from django.http import JsonResponse
from colegios.models import Clase, Asignacion, ClaseParticular
from configuracion.models import Profesor, Libro
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# CONSTANTES DE NEGOCIO
# Importadas desde colegios.views para no duplicarlas.
# Si en el futuro cambian, solo se tocan en un lugar.
# ─────────────────────────────────────────────────────────────
from colegios.views import UNIDADES_ESPECIALES


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────
def extraer_minutos(hora_str):
    """Convierte '8:00 - 10:00' en minutos para ordenar por hora."""
    try:
        partes = hora_str.split('-')[0].strip().split(':')
        return int(partes[0]) * 60 + int(partes[1])
    except (ValueError, IndexError, AttributeError):
        return 0


def _resolver_unidad(unidad, unidad_obj):
    """
    Centraliza la lógica de presentación de unidades.
    Devuelve (material_label, unidad_label, unidad_link).

    - 'A' → Material Asignado  / Banco de Preguntas
    - 'S' → Socialización de Simulacro / Socialización de Simulacro
    - N   → usa el objeto Libro para obtener nombre y link reales
    """
    unidad_str = str(unidad) if unidad else ''

    if unidad_str in UNIDADES_ESPECIALES:
        label = UNIDADES_ESPECIALES[unidad_str]
        # Para 'A' el material y la unidad tienen nombres distintos
        if unidad_str == 'A':
            return 'Material Asignado', 'Banco de Preguntas', '#'
        return label, label, '#'

    # Unidad numérica normal
    if unidad_obj:
        return None, f"{unidad}. {unidad_obj.nombre_unidad}", unidad_obj.link_unidad or '#'
    return None, str(unidad), '#'


def _construir_entrada_clase(c, libro_titulo):
    """
    Construye el dict estándar que el template espera para una clase de colegio.
    Evita repetir la misma estructura en varios lugares.
    """
    unidad_obj = Libro.objects.filter(
        titulo=libro_titulo, materia=c.materia, unidad=c.unidad
    ).first()

    material_override, unidad_full, unidad_link = _resolver_unidad(c.unidad, unidad_obj)

    return {
        # Pasamos el objeto Clase real; el template accede a c.colegio, c.bloque, etc.
        'clase':       c,
        'minutos':     extraer_minutos(c.bloque.hora),
        'material':    material_override if material_override else libro_titulo,
        'unidad_full': unidad_full,
        'unidad_link': unidad_link,
        'maps_link':   getattr(c.colegio, 'mapa_link', '#') or '#',
        'es_particular': False,
    }


def _construir_entrada_particular(p):
    """
    Construye el dict estándar para una ClaseParticular.
    NOTA: usamos un dict plano en lugar de un objeto falso para no
    confundir al lector. El template distingue por 'es_particular'.
    """
    unidad_obj = Libro.objects.filter(
        titulo=p.material, materia=p.materia, unidad=p.unidad
    ).first()

    material_override, unidad_full, unidad_link = _resolver_unidad(p.unidad, unidad_obj)

    return {
        # Datos normalizados que el template necesita
        'particular_obj': p,                           # objeto real para acceder a todos sus campos
        'minutos':        extraer_minutos(p.hora),
        'material':       material_override if material_override else p.material,
        'unidad_full':    unidad_full,
        'unidad_link':    unidad_link,
        'maps_link':      p.mapa_link or '#',
        'es_particular':  True,
        'particular_id':  p.id,
        # raw_data solo para inyectar en el modal de edición
        'raw_data': {
            'estudiante': p.estudiante,
            'ciudad':     p.ciudad,
            'mapa_link':  p.mapa_link or '',
            'fecha':      p.fecha.strftime('%Y-%m-%d'),
            'hora':       p.hora,
            'grado':      p.grado,
            'materia':    p.materia,
            'unidad':     p.unidad,
        },
    }


# ─────────────────────────────────────────────────────────────
# VISTAS AJAX
# ─────────────────────────────────────────────────────────────
def obtener_asignaturas_particular(request):
    material = request.GET.get('material')
    if not material:
        return JsonResponse([], safe=False)
    asignaturas = list(
        Libro.objects.filter(titulo=material)
        .values_list('materia', flat=True)
        .distinct()
    )
    return JsonResponse(asignaturas, safe=False)


def obtener_unidades_particular(request):
    material = request.GET.get('material')
    materia  = request.GET.get('materia')
    if not (material and materia):
        return JsonResponse([], safe=False)
    unidades = list(
        Libro.objects.filter(titulo=material, materia=materia)
        .values('unidad', 'nombre_unidad')
    )
    return JsonResponse(unidades, safe=False)


# ─────────────────────────────────────────────────────────────
# VISTA PRINCIPAL
# ─────────────────────────────────────────────────────────────
def ver_horario(request):
    # ── POST: guardar / editar / eliminar clase particular ──
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
                unidad=request.POST.get('unidad'),
            )
        elif 'editar_particular' in request.POST:
            ClaseParticular.objects.filter(
                id=request.POST.get('particular_id')
            ).update(
                estudiante=request.POST.get('estudiante'),
                ciudad=request.POST.get('ciudad'),
                mapa_link=request.POST.get('mapa_link'),
                fecha=request.POST.get('fecha'),
                hora=request.POST.get('hora'),
                grado=request.POST.get('grado'),
                material=request.POST.get('material'),
                materia=request.POST.get('materia'),
                unidad=request.POST.get('unidad'),
            )
        elif 'eliminar_particular' in request.POST:
            ClaseParticular.objects.filter(
                id=request.POST.get('particular_id')
            ).delete()

        return redirect(f"{request.path}?profesor_id={profesor_id}")

    # ── GET: mostrar horario ──
    profesor_id  = request.GET.get('profesor_id')
    profesores   = Profesor.objects.all().order_by('nombre')
    todos_libros = Libro.objects.values_list('titulo', flat=True).distinct()
    agrupado_por_fecha = []

    if profesor_id:
        temp_dict = defaultdict(list)

        # 1. Clases de colegios
        # select_related evita N+1 para colegio y bloque.
        # La consulta de Asignacion y Libro dentro del bucle se mantiene
        # porque depende del grado específico de cada clase.
        clases = (
            Clase.objects
            .filter(profesor_id=profesor_id, cancelada=False, es_evento=False)
            .select_related('colegio', 'bloque')
            .order_by('fecha')
        )

        # Precargamos todas las asignaciones del profesor de una sola vez
        # para evitar una consulta por cada clase.
        colegios_ids = clases.values_list('colegio_id', flat=True).distinct()
        asignaciones_map = {
            (a.colegio_id, a.grado): a.libro_titulo
            for a in Asignacion.objects.filter(colegio_id__in=colegios_ids)
        }

        for c in clases:
            libro_titulo = asignaciones_map.get(
                (c.colegio_id, c.bloque.grado), 'Sin Libro'
            )
            temp_dict[c.fecha].append(_construir_entrada_clase(c, libro_titulo))

        # 2. Clases particulares
        particulares = (
            ClaseParticular.objects
            .filter(profesor_id=profesor_id)
            .order_by('fecha')
        )
        for p in particulares:
            temp_dict[p.fecha].append(_construir_entrada_particular(p))

        # 3. Ordenar por fecha y luego por hora
        for fecha in sorted(temp_dict.keys()):
            clases_del_dia = sorted(temp_dict[fecha], key=lambda x: x['minutos'])
            agrupado_por_fecha.append({
                'fecha':    fecha,
                'cantidad': len(clases_del_dia),
                'clases':   clases_del_dia,
            })

    return render(request, 'profesores/horario.html', {
        'profesores':   profesores,
        'agrupado':     agrupado_por_fecha,
        'profesor_sel': profesor_id,
        'todos_libros': todos_libros,
    })