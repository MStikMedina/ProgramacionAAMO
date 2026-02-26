from django.shortcuts import render
from django.db.models import Prefetch
from cronograma.models import Bloque, Clase
from gestion_datos.models import Colegio
from datetime import date, timedelta, datetime
from collections import defaultdict
import re

# Reutilizamos las funciones auxiliares de ordenamiento
def extraer_numero_grado(grado_str):
    nums = re.findall(r'\d+', grado_str)
    return int(nums[0]) if nums else 0

def extraer_minutos(hora_str):
    try:
        h = hora_str.split('-')[0].strip().split(':')
        return int(h[0]) * 60 + int(h[1])
    except:
        return 0

def vista_general(request):
    # --- 1. LÓGICA DE FECHAS (Idéntica al cronograma individual) ---
    tipo_vista = request.GET.get('vista', 'Semana')
    fecha_get = request.GET.get('fecha')
    fecha_ref = datetime.strptime(fecha_get, '%Y-%m-%d').date() if fecha_get else date.today()
    
    if tipo_vista == 'Semana':
        inicio = fecha_ref - timedelta(days=fecha_ref.weekday())
        dias_totales = 7
    elif tipo_vista == 'Mes':
        inicio = fecha_ref.replace(day=1)
        next_month = (inicio + timedelta(days=32)).replace(day=1)
        dias_totales = (next_month - inicio).days
    else: # Año
        inicio = date(fecha_ref.year, 1, 1)
        dias_totales = 366 if (fecha_ref.year % 4 == 0) else 365
        
    dias_header = [inicio + timedelta(days=i) for i in range(dias_totales)]
    fecha_fin = dias_header[-1]

    # --- 2. OBTENCIÓN Y ESTRUCTURACIÓN DE DATOS ---
    
    # Traemos TODOS los bloques, ordenados por colegio y luego por su orden interno
    todos_bloques = Bloque.objects.all().select_related('colegio').order_by('colegio__nombre', 'orden')
    
    # Agrupamos temporalmente: Colegio -> Grado -> Lista de Bloques
    temp_agrupado = defaultdict(lambda: defaultdict(list))
    for bloque in todos_bloques:
        temp_agrupado[bloque.colegio][bloque.grado].append(bloque)
        
    # Estructura final para la plantilla
    estructura_general = []
    
    # Ordenamos los colegios por nombre
    for colegio in sorted(temp_agrupado.keys(), key=lambda c: c.nombre):
        datos_colegio = {
            'colegio': colegio,
            'grados_data': [],
            'total_rowspan': 0 # Cuántas filas ocupará este colegio en total
        }
        
        grados_dict = temp_agrupado[colegio]
        # Ordenamos los grados numéricamente (ej: 11, 10, 9...)
        grados_ordenados = sorted(grados_dict.keys(), key=extraer_numero_grado, reverse=True)
        
        for grado in grados_ordenados:
            # Ordenamos los bloques por hora
            bloques_ordenados = sorted(grados_dict[grado], key=lambda x: extraer_minutos(x.hora))
            rowspan_grado = len(bloques_ordenados)
            
            datos_colegio['grados_data'].append({
                'nombre_grado': grado,
                'bloques': bloques_ordenados,
                'rowspan': rowspan_grado
            })
            datos_colegio['total_rowspan'] += rowspan_grado
            
        estructura_general.append(datos_colegio)

    # --- 3. MATRIZ DE CLASES (Lookup rápido) ---
    clases = Clase.objects.filter(fecha__range=[inicio, fecha_fin]).select_related('profesor')
    matriz = defaultdict(dict)
    for c in clases:
        matriz[c.bloque_id][str(c.fecha)] = c

    ctx = {
        'dias_header': dias_header,
        'estructura_general': estructura_general,
        'matriz': matriz,
        'tipo_vista': tipo_vista,
        'fecha_input': fecha_ref.strftime('%Y-%m-%d'),
        'fecha_ant': (inicio - timedelta(days=1)).strftime('%Y-%m-%d'),
        'fecha_sig': (inicio + timedelta(days=dias_totales)).strftime('%Y-%m-%d'),
    }
    return render(request, 'general/vista_general.html', ctx)