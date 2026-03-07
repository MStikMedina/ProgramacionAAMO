from django.db import models
from django.contrib.auth.models import User
from configuracion.models import Colegio, Profesor


class UsuarioColegio(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_colegio')
    colegio        = models.ForeignKey(Colegio, on_delete=models.CASCADE, related_name='usuarios')
    password_texto = models.CharField(max_length=255, verbose_name="Contraseña")

    class Meta:
        verbose_name        = "Usuario de Colegio"
        verbose_name_plural = "Usuarios de Colegios"

    def __str__(self):
        return f"{self.user.username} → {self.colegio.nombre}"


class UsuarioProfesor(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_profesor')
    profesor       = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='usuarios')
    password_texto = models.CharField(max_length=255, verbose_name="Contraseña")

    class Meta:
        verbose_name        = "Usuario de Profesor"
        verbose_name_plural = "Usuarios de Profesores"

    def __str__(self):
        return f"{self.user.username} → {self.profesor.nombre}"