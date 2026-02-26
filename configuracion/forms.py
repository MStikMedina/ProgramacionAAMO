from django import forms
from .models import Libro, Colegio, Profesor

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'materia', 'unidad', 'nombre_unidad', 'link_unidad']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Saberes 11 Oro'}),
            'materia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Matemáticas'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'nombre_unidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Funciones'}),
            'link_unidad': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

class ColegioForm(forms.ModelForm):
    class Meta:
        model = Colegio
        fields = ['nombre', 'ciudad', 'mapa_link']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Liceo Campestre'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bucaramanga'}),
            'mapa_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://maps.google...'}),
        }

class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ['nombre', 'documento', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1098...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'juan@email.com'}),
        }