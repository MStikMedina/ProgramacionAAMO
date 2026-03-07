from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Informe
from configuracion.models import Profesor, Colegio
import json


# ── AJAX: obtener informe existente (o vacío) para un clase_id ───────────────

@login_required
def obtener_informe(request):
    clase_id       = request.GET.get('clase_id')
    particular_id  = request.GET.get('particular_id')

    informe = None
    if clase_id:
        informe = Informe.objects.filter(clase_id=clase_id).first()
    elif particular_id:
        informe = Informe.objects.filter(clase_particular_id=particular_id).first()

    if informe:
        data = {
            'existe':          True,
            'informe_id':      informe.id,
            'colegio_nombre':  informe.colegio_nombre,
            'grado':           informe.grado,
            'fecha':           informe.fecha.strftime('%d/%m/%Y'),
            'materia':         informe.materia,
            'tematica':        informe.tematica,
            'material':        informe.material,
            'actividades':     informe.actividades,
            'fortalezas':      informe.fortalezas,
            'debilidades':     informe.debilidades,
            'recomendaciones': informe.recomendaciones,
            'bibliografia':    informe.bibliografia,
        }
    else:
        data = {'existe': False}

    return JsonResponse(data)


# ── AJAX: guardar informe ────────────────────────────────────────────────────

@login_required
@require_POST
def guardar_informe(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    clase_id      = body.get('clase_id')
    particular_id = body.get('particular_id')
    profesor_id   = body.get('profesor_id')

    if not profesor_id:
        return JsonResponse({'ok': False, 'error': 'Falta profesor_id'}, status=400)

    campos_texto = {
        'actividades':     body.get('actividades', '').strip(),
        'fortalezas':      body.get('fortalezas', '').strip(),
        'debilidades':     body.get('debilidades', '').strip(),
        'recomendaciones': body.get('recomendaciones', '').strip(),
        'bibliografia':    body.get('bibliografia', '').strip(),
    }

    if clase_id:
        informe, _ = Informe.objects.update_or_create(
            clase_id=clase_id,
            defaults={
                'profesor_id':    profesor_id,
                'colegio_nombre': body.get('colegio_nombre', ''),
                'grado':          body.get('grado', ''),
                'fecha':          body.get('fecha_iso'),
                'materia':        body.get('materia', ''),
                'tematica':       body.get('tematica', ''),
                'material':       body.get('material', ''),
                **campos_texto,
            }
        )
    elif particular_id:
        informe, _ = Informe.objects.update_or_create(
            clase_particular_id=particular_id,
            defaults={
                'profesor_id':    profesor_id,
                'colegio_nombre': body.get('colegio_nombre', ''),
                'grado':          body.get('grado', ''),
                'fecha':          body.get('fecha_iso'),
                'materia':        body.get('materia', ''),
                'tematica':       body.get('tematica', ''),
                'material':       body.get('material', ''),
                **campos_texto,
            }
        )
    else:
        return JsonResponse({'ok': False, 'error': 'Falta clase_id o particular_id'}, status=400)

    return JsonResponse({'ok': True, 'informe_id': informe.id})


# ── Vista de lista de informes ────────────────────────────────────────────────

@login_required
def lista_informes(request):
    # Restricción por perfil
    perfil_profesor = getattr(request, 'perfil_profesor', None)
    if perfil_profesor is None and hasattr(request.user, 'perfil_profesor'):
        try:
            perfil_profesor = request.user.perfil_profesor
        except Exception:
            perfil_profesor = None

    perfil_colegio = getattr(request, 'perfil_colegio', None)
    if perfil_colegio is None and hasattr(request.user, 'perfil_colegio'):
        try:
            perfil_colegio = request.user.perfil_colegio
        except Exception:
            perfil_colegio = None

    informes = Informe.objects.select_related('profesor').order_by('-fecha')

    # Filtrar según el tipo de usuario
    if perfil_profesor:
        informes = informes.filter(profesor=perfil_profesor.profesor)
    elif perfil_colegio:
        informes = informes.filter(colegio_nombre=perfil_colegio.colegio.nombre)

    # Filtros GET
    q_profesor  = request.GET.get('profesor', '')
    q_colegio   = request.GET.get('colegio', '')
    q_materia   = request.GET.get('materia', '')
    q_fecha_ini = request.GET.get('fecha_ini', '')
    q_fecha_fin = request.GET.get('fecha_fin', '')

    if q_profesor:
        informes = informes.filter(profesor_id=q_profesor)
    if q_colegio:
        informes = informes.filter(colegio_nombre=q_colegio)
    if q_materia:
        informes = informes.filter(materia=q_materia)
    if q_fecha_ini:
        informes = informes.filter(fecha__gte=q_fecha_ini)
    if q_fecha_fin:
        informes = informes.filter(fecha__lte=q_fecha_fin)

    # Solo completados (con actividades) o todos
    solo_completos = request.GET.get('completos', '')
    if solo_completos == '1':
        informes = informes.exclude(actividades='')

    profesores = Profesor.objects.order_by('nombre') if request.user.is_superuser else []

    # Listas dinámicas para los filtros dropdown — siempre desde la BD real
    colegios_lista = sorted(
        Colegio.objects.values_list('nombre', flat=True).distinct()
    )
    from configuracion.models import Libro
    materias_lista = sorted(
        Libro.objects.values_list('materia', flat=True).distinct()
    )

    return render(request, 'informes/lista.html', {
        'informes':         informes,
        'profesores':       profesores,
        'colegios_lista':   colegios_lista,
        'materias_lista':   materias_lista,
        'q_profesor':       q_profesor,
        'q_colegio':        q_colegio,
        'q_materia':        q_materia,
        'q_fecha_ini':      q_fecha_ini,
        'q_fecha_fin':      q_fecha_fin,
        'solo_completos':   solo_completos,
        'usuario_bloqueado': bool(perfil_profesor or perfil_colegio),
        'es_usuario_colegio': bool(perfil_colegio),
        'es_usuario_profesor': bool(perfil_profesor),
    })


# ── AJAX: eliminar informe ──────────────────────────────────────────────────

@login_required
def eliminar_informe(request, informe_id):
    if not request.user.is_superuser:
        return JsonResponse({'ok': False, 'error': 'Sin permiso'}, status=403)
    informe = get_object_or_404(Informe, id=informe_id)
    informe.delete()
    from django.contrib import messages
    messages.success(request, 'Informe eliminado correctamente.')
    from django.shortcuts import redirect
    return redirect('lista_informes')


# ── Vista detalle de un informe ───────────────────────────────────────────────

@login_required
def detalle_informe(request, informe_id):
    informe = get_object_or_404(Informe, id=informe_id)

    # Seguridad: usuario de profesor solo ve sus propios informes
    perfil_profesor = getattr(request, 'perfil_profesor', None)
    if perfil_profesor is None and hasattr(request.user, 'perfil_profesor'):
        try:
            perfil_profesor = request.user.perfil_profesor
        except Exception:
            perfil_profesor = None

    if perfil_profesor and informe.profesor != perfil_profesor.profesor:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    return render(request, 'informes/detalle.html', {'informe': informe})