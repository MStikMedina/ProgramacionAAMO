from django.shortcuts import render, redirect
from django.http import JsonResponse
from colegios.models import Clase, Asignacion, ClaseParticular
from configuracion.models import Profesor, Libro
from collections import defaultdict

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


def _libro_para_fecha(asignaciones_por_clave, colegio_id, grado, fecha):
    """
    Recibe el dict (colegio_id, grado) → [lista de Asignacion] y devuelve
    el título del libro cuya asignación cubre la fecha dada.
    Retorna 'Sin Libro' si ninguna asignación cubre esa fecha.
    """
    for a in asignaciones_por_clave.get((colegio_id, grado), []):
        # El modelo garantiza que fecha_inicio y fecha_fin siempre tienen valor
        # (se autocompletan en Asignacion.save()), pero por robustez lo chequeamos.
        inicio = a.fecha_inicio
        fin    = a.fecha_fin
        if inicio and fin and inicio <= fecha <= fin:
            return a.libro_titulo
        if inicio is None and fin is None:
            return a.libro_titulo
    return 'Sin Libro'


def _resolver_unidad(unidad, unidad_obj):
    """
    Devuelve (material_label, unidad_label, unidad_link).
    - 'A' → Material Asignado / Banco de Preguntas
    - 'S' → Socialización de Simulacro
    - N   → usa el objeto Libro para nombre y link reales
    """
    unidad_str = str(unidad) if unidad else ''

    if unidad_str in UNIDADES_ESPECIALES:
        label = UNIDADES_ESPECIALES[unidad_str]
        if unidad_str == 'A':
            return 'Material Asignado', 'Banco de Preguntas', '#'
        return label, label, '#'

    if unidad_obj:
        return None, f"{unidad}. {unidad_obj.nombre_unidad}", unidad_obj.link_unidad or '#'
    return None, str(unidad), '#'


def _construir_entrada_clase(c, libro_titulo, libros_map=None):
    if libros_map is not None:
        unidad_obj = libros_map.get((libro_titulo, c.materia or '', str(c.unidad or '')))
    else:
        unidad_obj = Libro.objects.filter(
            titulo=libro_titulo, materia=c.materia, unidad=c.unidad
        ).first()

    material_override, unidad_full, unidad_link = _resolver_unidad(c.unidad, unidad_obj)

    return {
        'clase':         c,
        'minutos':       extraer_minutos(c.bloque.hora),
        'material':      material_override if material_override else libro_titulo,
        'unidad_full':   unidad_full,
        'unidad_link':   unidad_link,
        'maps_link':     getattr(c.colegio, 'mapa_link', '#') or '#',
        'es_particular': False,
    }


def _construir_entrada_particular(p, libros_map=None):
    if libros_map is not None:
        unidad_obj = libros_map.get((p.material or '', p.materia or '', str(p.unidad or '')))
    else:
        unidad_obj = Libro.objects.filter(
            titulo=p.material, materia=p.materia, unidad=p.unidad
        ).first()

    material_override, unidad_full, unidad_link = _resolver_unidad(p.unidad, unidad_obj)

    return {
        'particular_obj': p,
        'minutos':        extraer_minutos(p.hora),
        'material':       material_override if material_override else p.material,
        'unidad_full':    unidad_full,
        'unidad_link':    unidad_link,
        'maps_link':      p.mapa_link or '#',
        'es_particular':  True,
        'particular_id':  p.id,
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
    # Si es usuario de profesor, bloquear al profesor asignado
    perfil_profesor = getattr(request, 'perfil_profesor', None)
    if perfil_profesor is None and hasattr(request.user, 'perfil_profesor'):
        try:
            perfil_profesor = request.user.perfil_profesor
        except Exception:
            perfil_profesor = None

    if perfil_profesor:
        # Forzar siempre el profesor asignado, ignorando cualquier parámetro de URL
        profesor_id = str(perfil_profesor.profesor.id)
    else:
        profesor_id = request.GET.get('profesor_id')

    profesores   = Profesor.objects.all().order_by('nombre')
    todos_libros = Libro.objects.values_list('titulo', flat=True).distinct()
    agrupado_por_fecha = []
    usuario_bloqueado  = bool(perfil_profesor)

    if profesor_id:
        temp_dict = defaultdict(list)

        # 1. Clases de colegios
        clases = (
            Clase.objects
            .filter(profesor_id=profesor_id, cancelada=False, es_evento=False)
            .select_related('colegio', 'bloque')
            .order_by('fecha')
        )

        # ── CORRECCIÓN: cargamos TODAS las asignaciones de los colegios
        # relevantes como una lista por clave (colegio_id, grado), para
        # poder luego buscar la que corresponde a la FECHA de cada clase.
        colegios_ids = clases.values_list('colegio_id', flat=True).distinct()
        asignaciones_por_clave = defaultdict(list)
        for a in Asignacion.objects.filter(colegio_id__in=colegios_ids):
            asignaciones_por_clave[(a.colegio_id, a.grado)].append(a)

        # Pre-cargar todos los libros en memoria para evitar N+1
        libros_map = {
            (l.titulo, l.materia, str(l.unidad)): l
            for l in Libro.objects.all()
        }

        for c in clases:
            libro_titulo = _libro_para_fecha(
                asignaciones_por_clave, c.colegio_id, c.bloque.grado, c.fecha
            )
            temp_dict[c.fecha].append(_construir_entrada_clase(c, libro_titulo, libros_map))

        # 2. Clases particulares
        particulares = (
            ClaseParticular.objects
            .filter(profesor_id=profesor_id)
            .order_by('fecha')
        )
        for p in particulares:
            temp_dict[p.fecha].append(_construir_entrada_particular(p, libros_map))

        # 3. Ordenar por fecha y luego por hora
        for fecha in sorted(temp_dict.keys()):
            clases_del_dia = sorted(temp_dict[fecha], key=lambda x: x['minutos'])
            agrupado_por_fecha.append({
                'fecha':    fecha,
                'cantidad': len(clases_del_dia),
                'clases':   clases_del_dia,
            })

    return render(request, 'profesores/horario.html', {
        'profesores':        profesores,
        'agrupado':          agrupado_por_fecha,
        'profesor_sel':      profesor_id,
        'todos_libros':      todos_libros,
        'usuario_bloqueado': usuario_bloqueado,
    })