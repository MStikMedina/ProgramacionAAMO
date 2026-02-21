from django.contrib import admin
from django import forms
from gestion_datos.models import Libro
from .models import Bloque, Clase, Asignacion

@admin.register(Bloque)
class BloqueAdmin(admin.ModelAdmin):
    list_display = ('colegio', 'grado', 'hora', 'orden')
    list_filter = ('colegio', 'grado')
    search_fields = ('colegio__nombre', 'grado')

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'colegio', 'bloque', 'profesor', 'materia')
    list_filter = ('fecha', 'colegio', 'profesor')

class AsignacionForm(forms.ModelForm):
    libro_titulo = forms.ChoiceField(label="Libro", required=True)
    grado = forms.ChoiceField(label="Grado", required=True, choices=[('', '---------')])

    class Meta:
        model = Asignacion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar solo títulos de libros sin repetir
        libros_unicos = Libro.objects.values_list('titulo', 'titulo').distinct()
        self.fields['libro_titulo'].choices = [('', '---------')] + list(libros_unicos)
        
        # Mantener los grados cargados dinámicamente
        if 'colegio' in self.data:
            try:
                colegio_id = int(self.data.get('colegio'))
                grados = Bloque.objects.filter(colegio_id=colegio_id).values_list('grado', flat=True).distinct()
                self.fields['grado'].choices = [('', '---------')] + [(g, g) for g in grados]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            grados = Bloque.objects.filter(colegio=self.instance.colegio).values_list('grado', flat=True).distinct()
            self.fields['grado'].choices = [('', '---------')] + [(g, g) for g in grados]

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    form = AsignacionForm
    list_display = ('colegio', 'grado', 'libro_titulo')
    list_filter = ('colegio', 'libro_titulo')

    class Media:
        js = ('js/admin_asignacion.js',)