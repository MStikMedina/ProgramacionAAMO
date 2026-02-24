from django.shortcuts import render, redirect
from .models import Libro, Colegio, Profesor
from .forms import LibroForm, ColegioForm, ProfesorForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404

@user_passes_test(lambda u: u.is_superuser)
def gestion_libros(request):
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
        return redirect('gestion_libros')

    libros = Libro.objects.all().order_by('titulo', 'materia', 'unidad')
    return render(request, 'gestion_datos/libros.html', {'libros': libros})

@user_passes_test(lambda u: u.is_superuser)
def gestion_colegios(request):
    if request.method == 'POST':
        form = ColegioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_colegios')
    else:
        form = ColegioForm()
    
    colegios = Colegio.objects.all().order_by('nombre')
    return render(request, 'gestion_datos/colegios.html', {'form': form, 'colegios': colegios})

@user_passes_test(lambda u: u.is_superuser)
def gestion_profesores(request):
    if request.method == 'POST':
        accion = request.POST.get('accion', 'add') # Por defecto es add si no se envía
        
        if accion == 'edit':
            p = get_object_or_404(Profesor, id=request.POST.get('profesor_id'))
            p.nombre = request.POST.get('nombre')
            p.documento = request.POST.get('documento')
            p.email = request.POST.get('email')
            p.save()
        elif accion == 'del':
            Profesor.objects.filter(id=request.POST.get('profesor_id')).delete()
        else: # Lógica normal de agregar
            Profesor.objects.create(
                nombre=request.POST.get('nombre'),
                documento=request.POST.get('documento'),
                email=request.POST.get('email')
            )
        return redirect('gestion_profesores')

    profesores = Profesor.objects.all().order_by('nombre')
    return render(request, 'gestion_datos/profesores.html', {'profesores': profesores})