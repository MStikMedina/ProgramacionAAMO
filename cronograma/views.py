from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from datetime import date, timedelta, datetime
from collections import defaultdict
import re
import json
from gestion_datos.models import Colegio, Profesor, Libro
from .models import Bloque, Clase, Asignacion
from django.views.decorators.clickjacking import xframe_options_sameorigin

def extraer_minutos(hora_str):
    match = re.search(r'(\d+):(\d+)', str(hora_str))
    if match:
        h, m = map(int, match.groups())
        return h * 60 + m
    return 9999

def cargar_grados(request):
    colegio_id = request.GET.get('colegio_id')
    if colegio_id:
        grados = Bloque.objects.filter(colegio_id=colegio_id).values_list('grado', flat=True).distinct()
        return JsonResponse(list(grados), safe=False)
    return JsonResponse([], safe=False)

def obtener_materias(request):
    colegio_id = request.GET.get('colegio_id')
    grado = request.GET.get('grado')
    fecha_str = request.GET.get('fecha')
    
    if not all([colegio_id, grado, fecha_str]):
        return JsonResponse([])
        
    fecha_clase = datetime.strptime(fecha_str, '%Y-%m-%d').date()

    # Buscar libros asignados activos en esa fecha específica
    asignaciones = Asignacion.objects.filter(
        colegio_id=colegio_id,
        grado=grado,
        fecha_inicio__lte=fecha_clase,
        fecha_fin__gte=fecha_clase
    )
    
    materias = []
    for asig in asignaciones:
        mats = Libro.objects.filter(titulo=asig.libro_titulo).values_list('materia', flat=True).distinct()
        materias.extend(list(mats))
        
    return JsonResponse(list(set(materias)), safe=False)

def obtener_unidades(request):
    colegio_id = request.GET.get('colegio_id')
    grado = request.GET.get('grado')
    fecha_str = request.GET.get('fecha')
    materia = request.GET.get('materia')
    bloque_id = request.GET.get('bloque_id') # Nuevo parámetro

    if not all([colegio_id, grado, fecha_str, materia]):
        return JsonResponse({'unidades': [], 'recomendada': ''})

    fecha_clase = datetime.strptime(fecha_str, '%Y-%m-%d').date()

    asignaciones = Asignacion.objects.filter(
        colegio_id=colegio_id, grado=grado, fecha_inicio__lte=fecha_clase, fecha_fin__gte=fecha_clase
    )
    
    unidades_libro = []
    for asig in asignaciones:
        unis = Libro.objects.filter(titulo=asig.libro_titulo, materia=materia).values_list('unidad', flat=True)
        unidades_libro.extend(list(unis))

    # Extraer solo números para la recomendación
    numeros = sorted([str(u) for u in set(unidades_libro) if str(u).isdigit()], key=int)
    # Las unidades finales que se muestran en la lista sí incluyen A y S
    unidades_finales = numeros + ['A', 'S']

    unidad_recomendada = ""

    # Buscar el historial de la materia, sin importar el profesor
    query_clases = Clase.objects.filter(
        colegio_id=colegio_id,
        bloque__grado=grado,
        materia=materia,
        fecha__lte=fecha_clase # Incluimos la fecha actual para que lea clases del mismo día
    )

    if bloque_id:
        # Excluimos la celda actual que estamos editando para no romper la secuencia
        query_clases = query_clases.exclude(bloque_id=bloque_id, fecha=fecha_clase)

    # Obtenemos la última clase registrada
    ultima_clase = query_clases.order_by('-fecha', '-bloque__orden', '-id').first()

    if ultima_clase and ultima_clase.unidad and str(ultima_clase.unidad).isdigit():
        siguiente = str(int(ultima_clase.unidad) + 1)
        # Al validar que "siguiente" esté en "numeros", nos aseguramos de NUNCA recomendar A o S
        if siguiente in numeros: 
            unidad_recomendada = siguiente
    elif numeros:
        unidad_recomendada = numeros[0]

    return JsonResponse({
        'unidades': unidades_finales,
        'recomendada': unidad_recomendada
    })
    
def dashboard_cronograma(request):
    colegios = Colegio.objects.all().order_by('nombre')
    
    id_col = request.GET.get('id_col')
    tipo_vista = request.GET.get('vista', 'Semana')
    fecha_get = request.GET.get('fecha')
    fecha_ref = datetime.strptime(fecha_get, '%Y-%m-%d').date() if fecha_get else date.today()

    ctx = {
        'colegios': colegios,
        'sel_col': None,
        'tipo_vista': tipo_vista,
        'fecha_ref': fecha_ref,
        'fecha_input': fecha_ref.strftime('%Y-%m-%d'),
        'profesores': Profesor.objects.all().order_by('nombre'),
        'recursos_json': '{}', # Por defecto vacío
    }

    if id_col:
        sel_col = get_object_or_404(Colegio, id=id_col)
        ctx['sel_col'] = sel_col

        # --- PROCESAR GUARDADO O ELIMINACIÓN DE CLASE ---
        if request.method == "POST" and 'guardar_clase' in request.POST:
            bloque_id = request.POST.get('bloque_id')
            fecha_clase = request.POST.get('fecha_clase')
            eliminar = request.POST.get('eliminar_clase')

            if eliminar == "1":
                Clase.objects.filter(colegio=sel_col, bloque_id=bloque_id, fecha=fecha_clase).delete()
            else:
                profesor_id = request.POST.get('profesor')
                Clase.objects.update_or_create(
                    colegio=sel_col,
                    bloque_id=bloque_id,
                    fecha=fecha_clase,
                    defaults={
                        'profesor_id': profesor_id if profesor_id else None,
                        'materia': request.POST.get('materia'),
                        'unidad': request.POST.get('unidad')
                    }
                )
            return redirect(request.get_full_path())
        
        # --- LÓGICA DE RANGOS DE FECHA ---
        if tipo_vista == 'Semana':
            inicio = fecha_ref - timedelta(days=fecha_ref.weekday())
            dias_totales = 7
        elif tipo_vista == 'Mes':
            inicio = fecha_ref.replace(day=1)
            next_month = (inicio + timedelta(days=32)).replace(day=1)
            dias_totales = (next_month - inicio).days
        else:
            inicio = date(fecha_ref.year, 1, 1)
            dias_totales = 366 if (fecha_ref.year % 4 == 0) else 365
            
        dias_header = [inicio + timedelta(days=i) for i in range(dias_totales)]
        ctx.update({
            'dias_header': dias_header,
            'fecha_ant': (inicio - timedelta(days=1)).strftime('%Y-%m-%d'),
            'fecha_sig': (inicio + timedelta(days=dias_totales)).strftime('%Y-%m-%d'),
        })

        # --- ORDENAMIENTO DE BLOQUES ---
        bloques_raw = Bloque.objects.filter(colegio=sel_col)
        bloques_temp = defaultdict(list)
        for b in bloques_raw:
            bloques_temp[b.grado].append(b)
        
        def extraer_numero_grado(grado_str):
            nums = re.findall(r'\d+', grado_str)
            return int(nums[0]) if nums else 0

        grados_ordenados = sorted(bloques_temp.keys(), key=extraer_numero_grado, reverse=True)
        bloques_final = {}
        for grado in grados_ordenados:
            bloques_final[grado] = sorted(bloques_temp[grado], key=lambda x: extraer_minutos(x.hora))
        
        ctx['bloques_agrupados'] = bloques_final

        # --- MATRIZ DE CLASES ---
        clases = Clase.objects.filter(colegio=sel_col, fecha__range=[inicio, dias_header[-1]])
        matriz = {b.id: {} for b in bloques_raw}
        for c in clases:
            if c.bloque_id in matriz:
                matriz[c.bloque_id][str(c.fecha)] = c
        ctx['matriz'] = matriz

    return render(request, 'cronograma/dashboard.html', ctx)

@xframe_options_sameorigin
def configurar_colegio(request, colegio_id):
    colegio = get_object_or_404(Colegio, id=colegio_id)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        # --- Lógica para Bloques ---
        if accion == 'add_bloque':
            Bloque.objects.create(
                colegio=colegio,
                grado=request.POST.get('grado'),
                hora=request.POST.get('hora'),
                orden=request.POST.get('orden', 0)
            )
        elif accion == 'edit_bloque':
            b = get_object_or_404(Bloque, id=request.POST.get('bloque_id'), colegio=colegio)
            b.grado = request.POST.get('grado')
            b.hora = request.POST.get('hora')
            b.orden = request.POST.get('orden', 0)
            b.save()  # Guarda los cambios sin crear uno nuevo, protegiendo las clases
        elif accion == 'del_bloque':
            Bloque.objects.filter(id=request.POST.get('bloque_id')).delete()
            
        # --- Lógica para Asignaciones ---
        elif accion == 'add_asignacion':
            Asignacion.objects.create(
                colegio=colegio,
                grado=request.POST.get('grado'),
                libro_titulo=request.POST.get('libro_titulo'),
                fecha_inicio=request.POST.get('fecha_inicio') or None,
                fecha_fin=request.POST.get('fecha_fin') or None
            )
        elif accion == 'edit_asignacion':
            a = get_object_or_404(Asignacion, id=request.POST.get('asignacion_id'), colegio=colegio)
            a.grado = request.POST.get('grado')
            a.libro_titulo = request.POST.get('libro_titulo')
            a.fecha_inicio = request.POST.get('fecha_inicio') or None
            a.fecha_fin = request.POST.get('fecha_fin') or None
            a.save()
        elif accion == 'del_asignacion':
            Asignacion.objects.filter(id=request.POST.get('asignacion_id')).delete()
            
        return redirect('configurar_colegio', colegio_id=colegio.id)

    bloques = Bloque.objects.filter(colegio=colegio).order_by('grado', 'orden')
    asignaciones = Asignacion.objects.filter(colegio=colegio).order_by('grado')
    libros_unicos = Libro.objects.values_list('titulo', flat=True).distinct()

    return render(request, 'cronograma/configurar_colegio.html', {
        'colegio': colegio,
        'bloques': bloques,
        'asignaciones': asignaciones,
        'libros': libros_unicos
    })