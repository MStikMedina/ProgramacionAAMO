from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from datetime import date, timedelta, datetime
from collections import defaultdict
import re
import json
from gestion_datos.models import Colegio, Profesor, Libro
from .models import Bloque, Clase, Asignacion

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

        # --- VINCULACIÓN DE LIBROS PARA EL MODAL ---
        recursos_por_grado = defaultdict(list)
        asignaciones = Asignacion.objects.filter(colegio=sel_col)
        for asig in asignaciones:
            libros_detalle = Libro.objects.filter(titulo=asig.libro_titulo).order_by('materia', 'unidad')
            for lib in libros_detalle:
                texto = f"{lib.materia} - U.{lib.unidad} ({lib.nombre_unidad})"
                recursos_por_grado[asig.grado].append({
                    'materia': lib.materia,
                    'unidad': lib.unidad,
                    'texto': texto
                })
        ctx['recursos_json'] = json.dumps(recursos_por_grado)

    return render(request, 'cronograma/dashboard.html', ctx)