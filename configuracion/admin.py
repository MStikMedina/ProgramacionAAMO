from django.contrib import admin
from .models import Libro, Colegio, Profesor


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display  = ('titulo', 'materia', 'unidad', 'nombre_unidad')
    list_filter   = ('materia',)
    search_fields = ('titulo', 'materia', 'nombre_unidad')
    ordering      = ('titulo', 'materia', 'unidad')


@admin.register(Colegio)
class ColegioAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'ciudad', 'mapa_link')
    search_fields = ('nombre', 'ciudad')
    ordering      = ('nombre',)


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display  = ('nombre_corto', 'documento', 'email', 'celular', 'ciudad')
    search_fields = ('nombre', 'apellido', 'documento', 'email')
    list_filter   = ('ciudad', 'disponibilidad', 'banco')
    ordering      = ('nombre',)
    readonly_fields = ('nombre_corto',)