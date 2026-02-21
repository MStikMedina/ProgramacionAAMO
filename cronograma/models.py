from django.db import models

# Create your models here.
from django.db import models
from gestion_datos.models import Colegio, Profesor, Libro

class Bloque(models.Model):
    colegio = models.ForeignKey(Colegio, on_delete=models.CASCADE)
    hora = models.CharField(max_length=50)
    grado = models.CharField(max_length=50)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.grado} | {self.hora}"

class Asignacion(models.Model):
    colegio = models.ForeignKey(Colegio, on_delete=models.CASCADE)
    grado = models.CharField(max_length=50)
    libro_titulo = models.CharField(max_length=200, verbose_name="Libro")

    class Meta:
        verbose_name_plural = "Asignaciones de Libros"

    def __str__(self):
        return f"{self.colegio.nombre} - {self.grado} - {self.libro_titulo}"

class Clase(models.Model):
    colegio = models.ForeignKey(Colegio, on_delete=models.CASCADE)
    bloque = models.ForeignKey(Bloque, on_delete=models.CASCADE)
    fecha = models.DateField()
    profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, blank=True)
    materia = models.CharField(max_length=100, blank=True, null=True)
    unidad = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('fecha', 'bloque')