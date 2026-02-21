from django.shortcuts import render, redirect
from .models import Libro, Colegio, Profesor
from .forms import LibroForm, ColegioForm, ProfesorForm

def gestion_libros(request):
    if request.method == 'POST':
        form = LibroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_libros')
    else:
        form = LibroForm()

    libros = Libro.objects.all().order_by('titulo', 'materia', 'unidad')

    return render(request, 'gestion_datos/libros.html', {
        'form': form,
        'libros': libros
    })

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

def gestion_profesores(request):
    if request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_profesores')
    else:
        form = ProfesorForm()
    
    profesores = Profesor.objects.all().order_by('nombre')
    return render(request, 'gestion_datos/profesores.html', {'form': form, 'profesores': profesores})