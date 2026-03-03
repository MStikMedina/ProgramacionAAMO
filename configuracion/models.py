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

TIPO_CUENTA_CHOICES = [
    ('Ahorros', 'Ahorros'),
    ('Corriente', 'Corriente'),
]

ESTADO_CIVIL_CHOICES = [
    ('Soltero/a', 'Soltero/a'),
    ('Casado/a', 'Casado/a'),
    ('Unión libre', 'Unión libre'),
    ('Divorciado/a', 'Divorciado/a'),
    ('Viudo/a', 'Viudo/a'),
]

BANCOS_CHOISES = [
    ('Nequi', 'Nequi'),
    ('Bancolombia', 'Bancolombia'),
    ('Banco de Bogotá', 'Banco de Bogotá'),
    ('Davivienda', 'Davivienda'),
    ('Daviplata', 'Daviplata'),
    ('Nu', 'Nu'),
]

class Profesor(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre(s)")
    apellido = models.CharField(max_length=200, blank=True, null=True, verbose_name="Apellido(s)")
    documento = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Cédula / Documento")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    direccion = models.CharField(max_length=300, blank=True, null=True, verbose_name="Dirección")
    cuenta_bancaria = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cuenta Bancaria")
    banco = models.CharField(max_length=100, blank=True, null=True, choices=BANCOS_CHOISES, verbose_name="Banco")
    tipo_cuenta = models.CharField(max_length=20, blank=True, null=True, choices=TIPO_CUENTA_CHOICES, verbose_name="Tipo de Cuenta")
    area_materia = models.CharField(max_length=200, blank=True, null=True, verbose_name="Área / Materia que dicta")
    disponibilidad = models.CharField(max_length=50, blank=True, null=True, verbose_name="Disponibilidad")
    eps = models.CharField(max_length=100, blank=True, null=True, verbose_name="EPS")
    fondo_pension = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fondo de Pensión")
    estado_civil = models.CharField(max_length=20, blank=True, null=True, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado Civil")
    talla_camisa = models.CharField(max_length=10, blank=True, null=True, verbose_name="Talla Camisa")
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")

    @property
    def nombre_corto(self):
        primer_nombre = self.nombre.split()[0] if self.nombre else ''
        primer_apellido = self.apellido.split()[0] if self.apellido else ''
        return f"{primer_nombre} {primer_apellido}".strip()

    def __str__(self):
        return self.nombre_corto