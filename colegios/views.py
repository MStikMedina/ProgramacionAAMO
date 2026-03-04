from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from datetime import date, timedelta, datetime
from collections import defaultdict
import re
from configuracion.models import Colegio, Profesor, Libro
from .models import Bloque, Clase, Asignacion
from django.views.decorators.clickjacking import xframe_options_sameorigin

# ─────────────────────────────────────────────────────────────
# CONSTANTES DE NEGOCIO (fuente única de verdad)
# En lugar de tener "A", "S" hardcodeados en templates y views,
# los definimos aquí una sola vez.
# ─────────────────────────────────────────────────────────────
UNIDADES_ESPECIALES = {
    'A': 'Material Asignado',
    'S': 'Socialización de Simulacro',
}

def label_unidad(unidad):
    """Devuelve el texto legible de una unidad para mostrar en templates."""
    return UNIDADES_ESPECIALES.get(str(unidad), f'Unidad {unidad}')


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────
def extraer_minutos(hora_str):
    """Convierte '8:00 - 10:00' en minutos (480) para poder ordenar por hora."""
    match = re.search(r'(\d+):(\d+)', str(hora_str))
    if match:
        h, m = map(int, match.groups())
        return h * 60 + m
    return 9999


def extraer_numero_grado(grado_str):
    """Extrae el número de un grado ('11-1' → 11) para ordenar de mayor a menor."""
    nums = re.findall(r'\d+', grado_str)
    return int(nums[0]) if nums else 0


# ─────────────────────────────────────────────────────────────
# VISTAS AJAX
# ─────────────────────────────────────────────────────────────
def cargar_grados(request):
    colegio_id = request.GET.get('colegio_id')
    if colegio_id:
        grados = Bloque.objects.filter(
            colegio_id=colegio_id
        ).values_list('grado', flat=True).distinct()
        return JsonResponse(list(grados), safe=False)
    return JsonResponse([], safe=False)


def obtener_materias(request):
    colegio_id = request.GET.get('colegio_id')
    grado      = request.GET.get('grado')
    fecha_str  = request.GET.get('fecha')

    if not all([colegio_id, grado, fecha_str]):
        return JsonResponse([])

    try:
        fecha_clase = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse([])

    # Una sola consulta: asignaciones + libros en el mismo queryset
    asignaciones = Asignacion.objects.filter(
        colegio_id=colegio_id,
        grado=grado,
        fecha_inicio__lte=fecha_clase,
        fecha_fin__gte=fecha_clase,
    ).values_list('libro_titulo', flat=True)

    materias = list(
        Libro.objects.filter(titulo__in=asignaciones)
        .values_list('materia', flat=True)
        .distinct()
    )
    return JsonResponse(materias, safe=False)


def obtener_unidades(request):
    colegio_id = request.GET.get('colegio_id')
    grado      = request.GET.get('grado')
    fecha_str  = request.GET.get('fecha')
    materia    = request.GET.get('materia')
    bloque_id  = request.GET.get('bloque_id')

    if not all([colegio_id, grado, fecha_str, materia]):
        return JsonResponse({'unidades': [], 'recomendada': ''})

    try:
        fecha_clase = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'unidades': [], 'recomendada': ''})

    # Una sola consulta para obtener títulos de libros asignados
    titulos_asignados = Asignacion.objects.filter(
        colegio_id=colegio_id,
        grado=grado,
        fecha_inicio__lte=fecha_clase,
        fecha_fin__gte=fecha_clase,
    ).values_list('libro_titulo', flat=True)

    unidades_libro = list(
        Libro.objects.filter(titulo__in=titulos_asignados, materia=materia)
        .values_list('unidad', flat=True)
    )

    numeros = sorted(
        [str(u) for u in set(unidades_libro) if str(u).isdigit()], key=int
    )
    # Las unidades especiales siempre se agregan al final
    unidades_finales = numeros + list(UNIDADES_ESPECIALES.keys())

    # Calcular unidad recomendada
    unidad_recomendada = ''
    query_clases = Clase.objects.filter(
        colegio_id=colegio_id,
        bloque__grado=grado,
        materia=materia,
        fecha__lte=fecha_clase,
    )
    if bloque_id:
        query_clases = query_clases.exclude(bloque_id=bloque_id, fecha=fecha_clase)

    ultima_clase = query_clases.order_by('-fecha', '-bloque__orden', '-id').first()
    if ultima_clase and ultima_clase.unidad and str(ultima_clase.unidad).isdigit():
        siguiente = str(int(ultima_clase.unidad) + 1)
        if siguiente in numeros:
            unidad_recomendada = siguiente
    elif numeros:
        unidad_recomendada = numeros[0]

    return JsonResponse({'unidades': unidades_finales, 'recomendada': unidad_recomendada})


# ─────────────────────────────────────────────────────────────
# HELPERS PRIVADOS DE dashboard_colegios
# (vista dividida en funciones pequeñas y claras)
# ─────────────────────────────────────────────────────────────
def _guardar_clase(request, sel_col):
    """Procesa el POST de guardar o eliminar una clase."""
    bloque_id  = request.POST.get('bloque_id')
    fecha_clase = request.POST.get('fecha_clase')

    if request.POST.get('eliminar_clase') == '1':
        Clase.objects.filter(
            colegio=sel_col, bloque_id=bloque_id, fecha=fecha_clase
        ).delete()
        return

    profesor_id = request.POST.get('profesor') or None
    Clase.objects.update_or_create(
        colegio=sel_col,
        bloque_id=bloque_id,
        fecha=fecha_clase,
        defaults={
            'profesor_id': profesor_id,
            'materia':      request.POST.get('materia'),
            'unidad':       request.POST.get('unidad'),
            'es_evento':    request.POST.get('es_evento') == 'on',
            'titulo_evento': request.POST.get('titulo_evento'),
            'cancelada':    request.POST.get('cancelada') == 'on',
            'comentarios':  request.POST.get('comentarios'),
        }
    )


def _calcular_rango_fechas(tipo_vista, fecha_ref):
    """Devuelve (inicio, dias_totales) según la vista elegida."""
    if tipo_vista == 'Semana':
        inicio = fecha_ref - timedelta(days=fecha_ref.weekday())
        dias_totales = 7
    elif tipo_vista == 'Mes':
        inicio = fecha_ref.replace(day=1)
        next_month = (inicio + timedelta(days=32)).replace(day=1)
        dias_totales = (next_month - inicio).days
    else:  # Año
        inicio = date(fecha_ref.year, 1, 1)
        dias_totales = 366 if (fecha_ref.year % 4 == 0) else 365
    return inicio, dias_totales


def _construir_bloques_agrupados(sel_col):
    """Devuelve los bloques del colegio agrupados por grado y ordenados."""
    bloques_raw = Bloque.objects.filter(colegio=sel_col)
    bloques_temp = defaultdict(list)
    for b in bloques_raw:
        bloques_temp[b.grado].append(b)

    grados_ordenados = sorted(
        bloques_temp.keys(), key=extraer_numero_grado, reverse=True
    )
    return bloques_raw, {
        grado: sorted(bloques_temp[grado], key=lambda x: extraer_minutos(x.hora))
        for grado in grados_ordenados
    }


def _construir_matriz(sel_col, bloques_raw, inicio, fin):
    """Devuelve un dict {bloque_id: {fecha_str: clase}} para renderizar la tabla."""
    clases = Clase.objects.filter(
        colegio=sel_col, fecha__range=[inicio, fin]
    ).select_related('profesor')

    matriz = {b.id: {} for b in bloques_raw}
    for c in clases:
        if c.bloque_id in matriz:
            matriz[c.bloque_id][str(c.fecha)] = c
    return matriz


def _ejecutar_auditoria(nombre_sel):
    """
    Revisa todas las clases del año en busca de:
    - Unidades duplicadas por grado/materia
    - Profesores con conflicto de horario (mismo día, dos colegios)
    - Saltos en la secuencia de unidades
    Devuelve un dict con las tres listas de errores ordenadas.
    """
    año_actual = date.today().year
    todas_clases = (
        Clase.objects
        .filter(fecha__year=año_actual, es_evento=False, cancelada=False)
        .select_related('colegio', 'bloque', 'profesor')
        .order_by('fecha', 'bloque__orden', 'id')
    )

    mapa_unidades   = defaultdict(list)
    mapa_profesores = defaultdict(set)
    mapa_secuencia  = defaultdict(list)

    for c in todas_clases:
        if not c.materia or not c.unidad:
            continue
        grado      = c.bloque.grado
        col_nombre = c.colegio.nombre

        if str(c.unidad).isdigit():
            mapa_unidades[(col_nombre, grado, c.materia, c.unidad)].append(c)

        if c.profesor_id:
            mapa_profesores[(c.profesor.nombre_corto, c.fecha)].add(col_nombre)

        mapa_secuencia[(col_nombre, grado, c.materia)].append(c)

    # — Duplicados —
    errores_duplicados = []
    for (col, gr, mat, uni), clases_list in mapa_unidades.items():
        if len(clases_list) > 1:
            fechas = [cl.fecha.strftime('%d-%b') for cl in clases_list]
            errores_duplicados.append({
                'colegio': col,
                'mensaje': (
                    f"El grado {gr} tiene programada la unidad {uni} de {mat} "
                    f"{len(clases_list)} veces (Fechas: {', '.join(fechas)})."
                ),
            })

    # — Conflictos de profesor —
    errores_profesores = []
    for (profe_nombre, fecha), colegios_set in mapa_profesores.items():
        if len(colegios_set) > 1:
            lista = list(colegios_set)
            errores_profesores.append({
                'colegio': lista,
                'colegios_implicados': lista,
                'mensaje': (
                    f"El profesor {profe_nombre} tiene clases en {len(lista)} colegios "
                    f"distintos el {fecha.strftime('%d-%b')} ({' y '.join(lista)})."
                ),
            })

    # — Saltos de secuencia —
    errores_secuencias = []
    for (col, gr, mat), clases_list in mapa_secuencia.items():
        ultima_unidad = None
        for cl in clases_list:
            if str(cl.unidad).isdigit():
                unidad_actual = int(cl.unidad)
                if ultima_unidad is not None and (
                    unidad_actual > ultima_unidad + 1 or unidad_actual < ultima_unidad
                ):
                    errores_secuencias.append({
                        'colegio': col,
                        'mensaje': (
                            f"Salto de secuencia en el grado {gr} para {mat}. "
                            f"Pasó de la unidad {ultima_unidad} a la {unidad_actual} "
                            f"el {cl.fecha.strftime('%d-%b')}."
                        ),
                    })
                ultima_unidad = unidad_actual

    def _priorizar(err_list):
        """Pone primero los errores del colegio que se está viendo."""
        return sorted(
            err_list,
            key=lambda x: 0 if (
                x['colegio'] == nombre_sel or
                (x.get('colegios_implicados') and nombre_sel in x['colegios_implicados'])
            ) else 1
        )

    return {
        'errores_duplicados':  _priorizar(errores_duplicados),
        'errores_profesores':  _priorizar(errores_profesores),
        'errores_secuencias':  _priorizar(errores_secuencias),
    }


# ─────────────────────────────────────────────────────────────
# VISTA PRINCIPAL
# ─────────────────────────────────────────────────────────────
def dashboard_colegios(request):
    colegios   = Colegio.objects.all().order_by('nombre')
    id_col     = request.GET.get('id_col')
    tipo_vista = request.GET.get('vista', 'Semana')
    fecha_get  = request.GET.get('fecha')

    try:
        fecha_ref = datetime.strptime(fecha_get, '%Y-%m-%d').date() if fecha_get else date.today()
    except ValueError:
        fecha_ref = date.today()

    ctx = {
        'colegios':    colegios,
        'sel_col':     None,
        'tipo_vista':  tipo_vista,
        'fecha_ref':   fecha_ref,
        'fecha_input': fecha_ref.strftime('%Y-%m-%d'),
        'profesores':  Profesor.objects.all().order_by('nombre'),
        'recursos_json': '{}',
        # Pasamos las etiquetas de unidades especiales para que el template
        # no tenga lógica hardcodeada
        'unidades_especiales': UNIDADES_ESPECIALES,
    }

    if id_col:
        sel_col = get_object_or_404(Colegio, id=id_col)
        ctx['sel_col'] = sel_col

        if request.method == 'POST' and 'guardar_clase' in request.POST:
            if request.user.is_staff:
                _guardar_clase(request, sel_col)
            return redirect(request.get_full_path())

        inicio, dias_totales = _calcular_rango_fechas(tipo_vista, fecha_ref)
        dias_header = [inicio + timedelta(days=i) for i in range(dias_totales)]

        ctx.update({
            'dias_header': dias_header,
            'fecha_ant':   (inicio - timedelta(days=1)).strftime('%Y-%m-%d'),
            'fecha_sig':   (inicio + timedelta(days=dias_totales)).strftime('%Y-%m-%d'),
        })

        bloques_raw, bloques_agrupados = _construir_bloques_agrupados(sel_col)
        ctx['bloques_agrupados'] = bloques_agrupados
        ctx['matriz'] = _construir_matriz(sel_col, bloques_raw, inicio, dias_header[-1])

    if request.user.is_staff:
        nombre_sel = ctx['sel_col'].nombre if ctx.get('sel_col') else ''
        ctx.update(_ejecutar_auditoria(nombre_sel))

    return render(request, 'colegios/dashboard.html', ctx)


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE COLEGIO
# ─────────────────────────────────────────────────────────────
@xframe_options_sameorigin
def configurar_colegio(request, colegio_id):
    colegio = get_object_or_404(Colegio, id=colegio_id)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'add_bloque':
            Bloque.objects.create(
                colegio=colegio,
                grado=request.POST.get('grado'),
                hora=request.POST.get('hora'),
                orden=request.POST.get('orden', 0),
            )
        elif accion == 'edit_bloque':
            b = get_object_or_404(Bloque, id=request.POST.get('bloque_id'), colegio=colegio)
            b.grado = request.POST.get('grado')
            b.hora  = request.POST.get('hora')
            b.orden = request.POST.get('orden', 0)
            b.save()
        elif accion == 'del_bloque':
            Bloque.objects.filter(id=request.POST.get('bloque_id')).delete()
        elif accion == 'add_asignacion':
            Asignacion.objects.create(
                colegio=colegio,
                grado=request.POST.get('grado'),
                libro_titulo=request.POST.get('libro_titulo'),
                fecha_inicio=request.POST.get('fecha_inicio') or None,
                fecha_fin=request.POST.get('fecha_fin') or None,
            )
        elif accion == 'edit_asignacion':
            a = get_object_or_404(Asignacion, id=request.POST.get('asignacion_id'), colegio=colegio)
            a.grado        = request.POST.get('grado')
            a.libro_titulo = request.POST.get('libro_titulo')
            a.fecha_inicio = request.POST.get('fecha_inicio') or None
            a.fecha_fin    = request.POST.get('fecha_fin') or None
            a.save()
        elif accion == 'del_asignacion':
            Asignacion.objects.filter(id=request.POST.get('asignacion_id')).delete()

        return redirect('configurar_colegio', colegio_id=colegio.id)

    bloques      = Bloque.objects.filter(colegio=colegio).order_by('grado', 'orden')
    asignaciones = Asignacion.objects.filter(colegio=colegio).order_by('grado')
    libros_unicos = Libro.objects.values_list('titulo', flat=True).distinct()

    return render(request, 'colegios/configurar_colegio.html', {
        'colegio':     colegio,
        'bloques':     bloques,
        'asignaciones': asignaciones,
        'libros':      libros_unicos,
    })