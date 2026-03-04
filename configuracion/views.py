from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Libro, Colegio, Profesor
from .forms import LibroForm, ColegioForm, ProfesorForm

# Solo superusuarios pueden acceder a las vistas de configuración
solo_superusuario = user_passes_test(lambda u: u.is_superuser)


# ─────────────────────────────────────────────────────────────
# LIBROS
# ─────────────────────────────────────────────────────────────
@solo_superusuario
def configuracion_libros(request):
    if request.method == 'POST':
        accion = request.POST.get('accion', 'add')

        if accion == 'edit':
            # Usamos el form con la instancia existente para validar y guardar
            lib  = get_object_or_404(Libro, id=request.POST.get('libro_id'))
            form = LibroForm(request.POST, instance=lib)
            if form.is_valid():
                form.save()

        elif accion == 'del':
            Libro.objects.filter(id=request.POST.get('libro_id')).delete()

        else:  # add
            form = LibroForm(request.POST)
            if form.is_valid():
                form.save()

        return redirect('configuracion_libros')

    libros = Libro.objects.all().order_by('titulo', 'materia', 'unidad')
    return render(request, 'configuracion/libros.html', {
        'libros': libros,
        'form':   LibroForm(),   # form vacío para el panel de creación
    })


# ─────────────────────────────────────────────────────────────
# COLEGIOS
# ─────────────────────────────────────────────────────────────
@solo_superusuario
def configuracion_colegios(request):
    if request.method == 'POST':
        accion = request.POST.get('accion', 'add')

        if accion == 'edit':
            col  = get_object_or_404(Colegio, id=request.POST.get('colegio_id'))
            form = ColegioForm(request.POST, instance=col)
            if form.is_valid():
                form.save()

        elif accion == 'del':
            Colegio.objects.filter(id=request.POST.get('colegio_id')).delete()

        else:  # add
            form = ColegioForm(request.POST)
            if form.is_valid():
                form.save()

        return redirect('configuracion_colegios')

    colegios = Colegio.objects.all().order_by('nombre')
    return render(request, 'configuracion/colegios.html', {
        'form':     ColegioForm(),
        'colegios': colegios,
    })


# ─────────────────────────────────────────────────────────────
# PROFESORES
# ─────────────────────────────────────────────────────────────
@solo_superusuario
def configuracion_profesores(request):
    if request.method == 'POST':
        accion = request.POST.get('accion', 'add')

        if accion == 'edit':
            p    = get_object_or_404(Profesor, id=request.POST.get('profesor_id'))
            form = ProfesorForm(request.POST, instance=p)
            if form.is_valid():
                form.save()

        elif accion == 'del':
            Profesor.objects.filter(id=request.POST.get('profesor_id')).delete()

        else:  # add
            form = ProfesorForm(request.POST)
            if form.is_valid():
                form.save()

        return redirect('configuracion_profesores')

    profesores = Profesor.objects.all().order_by('nombre')
    return render(request, 'configuracion/profesores.html', {
        'profesores': profesores,
        'form':       ProfesorForm(),
    })