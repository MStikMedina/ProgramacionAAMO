from django.db import models
from configuracion.models import Profesor
from colegios.models import Clase, ClaseParticular


class Informe(models.Model):
    # ── Relación con la clase ────────────────────────────────────────────────
    profesor         = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='informes')
    clase            = models.OneToOneField(Clase, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='informe')
    clase_particular = models.OneToOneField(ClaseParticular, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='informe')

    # ── Campos auto-llenados desde la clase ──────────────────────────────────
    colegio_nombre   = models.CharField(max_length=200)
    grado            = models.CharField(max_length=50)
    fecha            = models.DateField()
    materia          = models.CharField(max_length=100)   # Área
    tematica         = models.CharField(max_length=200)   # Temática (unidad_full)
    material         = models.CharField(max_length=200)   # Material empleado

    # ── Campos que llena el profesor ─────────────────────────────────────────
    actividades      = models.TextField(blank=True, default='')
    fortalezas       = models.TextField(blank=True, default='')
    debilidades      = models.TextField(blank=True, default='')
    recomendaciones  = models.TextField(blank=True, default='')
    bibliografia     = models.TextField(blank=True, default='')

    # ── Auditoría ─────────────────────────────────────────────────────────────
    creado_en        = models.DateTimeField(auto_now_add=True)
    actualizado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Informe de Sesión'
        verbose_name_plural = 'Informes de Sesión'
        ordering            = ['-fecha', 'colegio_nombre']

    def __str__(self):
        return f"{self.fecha} | {self.profesor} | {self.colegio_nombre} {self.grado}"

    @property
    def completado(self):
        """True si el profesor ya llenó al menos Actividades."""
        return bool(self.actividades.strip())