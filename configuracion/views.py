from django.shortcuts import render, redirect, get_object_or_404
from .models import Libro, Colegio, Profesor
from .forms import LibroForm, ColegioForm, ProfesorForm
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def configuracion_libros(request):
    if request.method == 'POST':
        accion = request.POST.get('accion', 'add')
        if accion == 'edit':
            lib = get_object_or_404(Libro, id=request.POST.get('libro_id'))
            lib.titulo = request.POST.get('titulo')
            lib.materia = request.POST.get('materia')
            lib.unidad = request.POST.get('unidad')
            lib.nombre_unidad = request.POST.get('nombre_unidad')
            lib.link_unidad = request.POST.get('link_unidad')
            lib.save()
        elif accion == 'del':
            Libro.objects.filter(id=request.POST.get('libro_id')).delete()
        else:
            Libro.objects.create(
                titulo=request.POST.get('titulo'),
                materia=request.POST.get('materia'),
                unidad=request.POST.get('unidad'),
                nombre_unidad=request.POST.get('nombre_unidad'),
                link_unidad=request.POST.get('link_unidad')
            )
        return redirect('configuracion_libros')

    libros = Libro.objects.all().order_by('titulo', 'materia', 'unidad')
    return render(request, 'configuracion/libros.html', {'libros': libros})

@user_passes_test(lambda u: u.is_superuser)
def configuracion_colegios(request):
    if request.method == 'POST':
        form = ColegioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('configuracion_colegios')
    else:
        form = ColegioForm()
    colegios = Colegio.objects.all().order_by('nombre')
    return render(request, 'configuracion/colegios.html', {'form': form, 'colegios': colegios})

@user_passes_test(lambda u: u.is_superuser)
def configuracion_profesores(request):
    if request.method == 'POST':
        accion = request.POST.get('accion', 'add')

        campos = dict(
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            documento=request.POST.get('documento') or None,
            email=request.POST.get('email') or None,
            ciudad=request.POST.get('ciudad') or None,
            celular=request.POST.get('celular') or None,
            direccion=request.POST.get('direccion') or None,
            cuenta_bancaria=request.POST.get('cuenta_bancaria') or None,
            banco=request.POST.get('banco') or None,
            tipo_cuenta=request.POST.get('tipo_cuenta') or None,
            area_materia=request.POST.get('area_materia') or None,
            disponibilidad=request.POST.get('disponibilidad') or None,
            eps=request.POST.get('eps') or None,
            fondo_pension=request.POST.get('fondo_pension') or None,
            estado_civil=request.POST.get('estado_civil') or None,
            talla_camisa=request.POST.get('talla_camisa') or None,
            fecha_nacimiento=request.POST.get('fecha_nacimiento') or None,
        )

        if accion == 'edit':
            p = get_object_or_404(Profesor, id=request.POST.get('profesor_id'))
            for campo, valor in campos.items():
                setattr(p, campo, valor)
            p.save()
        elif accion == 'del':
            Profesor.objects.filter(id=request.POST.get('profesor_id')).delete()
        else:
            Profesor.objects.create(**campos)

        return redirect('configuracion_profesores')

    profesores = Profesor.objects.all().order_by('nombre')
    return render(request, 'configuracion/profesores.html', {'profesores': profesores})