from django.db import models
from gestion_datos.models import Colegio, Profesor, Libro
from datetime import date

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
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin")

    class Meta:
        verbose_name_plural = "Asignaciones de Libros"

    def save(self, *args, **kwargs):
        hoy = date.today()
        # Si no se seleccionan fechas, se asigna todo el año vigente automáticamente
        if not self.fecha_inicio:
            self.fecha_inicio = date(hoy.year, 1, 1)
        if not self.fecha_fin:
            self.fecha_fin = date(hoy.year, 12, 31)
        super().save(*args, **kwargs)

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