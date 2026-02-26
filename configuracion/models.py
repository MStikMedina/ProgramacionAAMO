from django.db import models

class Libro(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título del Libro")
    materia = models.CharField(max_length=100)
    unidad = models.CharField(max_length=50, verbose_name="Unidad / Número")
    nombre_unidad = models.CharField(max_length=200, verbose_name="Nombre de la Unidad")
    link_unidad = models.URLField(max_length=500, verbose_name="Link de la Unidad")

    def __str__(self):
        return f"{self.titulo} - {self.materia} (U.{self.unidad})"

class Colegio(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Colegio")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    mapa_link = models.URLField(blank=True, null=True, verbose_name="Link de Maps")
    
    def __str__(self):
        return self.nombre

class Profesor(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre Completo")
    documento = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Cédula / Documento")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    
    def __str__(self):
        return self.nombre