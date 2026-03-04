from django import forms
from .models import Libro, Colegio, Profesor


class LibroForm(forms.ModelForm):
    """Formulario completo para crear y editar libros."""
    class Meta:
        model  = Libro
        fields = ['titulo', 'materia', 'unidad', 'nombre_unidad', 'link_unidad']
        widgets = {
            'titulo':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Saberes 11 Oro'}),
            'materia':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Matemáticas'}),
            'unidad':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'nombre_unidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Funciones'}),
            'link_unidad':  forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }


class ColegioForm(forms.ModelForm):
    """Formulario para crear y editar colegios."""
    class Meta:
        model  = Colegio
        fields = ['nombre', 'ciudad', 'mapa_link']
        widgets = {
            'nombre':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Liceo Campestre'}),
            'ciudad':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bucaramanga'}),
            'mapa_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://maps.google...'}),
        }


class ProfesorForm(forms.ModelForm):
    """
    Formulario completo del profesor.
    Todos los campos opcionales usan required=False para respetar
    los blank=True / null=True del modelo.
    """
    class Meta:
        model  = Profesor
        fields = [
            # Datos personales
            'nombre', 'apellido', 'documento', 'fecha_nacimiento',
            'estado_civil', 'talla_camisa',
            # Contacto
            'email', 'celular', 'ciudad', 'direccion',
            # Laboral
            'area_materia', 'disponibilidad', 'eps', 'fondo_pension',
            # Bancario
            'banco', 'tipo_cuenta', 'cuenta_bancaria',
        ]
        widgets = {
            'nombre':           forms.TextInput(attrs={'class': 'form-control'}),
            'apellido':         forms.TextInput(attrs={'class': 'form-control'}),
            'documento':        forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado_civil':     forms.Select(attrs={'class': 'form-select'}),
            'talla_camisa':     forms.TextInput(attrs={'class': 'form-control'}),
            'email':            forms.EmailInput(attrs={'class': 'form-control'}),
            'celular':          forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad':           forms.TextInput(attrs={'class': 'form-control'}),
            'direccion':        forms.TextInput(attrs={'class': 'form-control'}),
            'area_materia':     forms.TextInput(attrs={'class': 'form-control'}),
            'disponibilidad':   forms.TextInput(attrs={'class': 'form-control'}),
            'eps':              forms.TextInput(attrs={'class': 'form-control'}),
            'fondo_pension':    forms.TextInput(attrs={'class': 'form-control'}),
            'banco':            forms.Select(attrs={'class': 'form-select'}),
            'tipo_cuenta':      forms.Select(attrs={'class': 'form-select'}),
            'cuenta_bancaria':  forms.TextInput(attrs={'class': 'form-control'}),
        }