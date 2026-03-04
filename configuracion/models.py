from django.db import models


class Libro(models.Model):
    titulo       = models.CharField(max_length=200, verbose_name="Título del Libro")
    materia      = models.CharField(max_length=100)
    unidad       = models.CharField(max_length=50, verbose_name="Unidad / Número")
    nombre_unidad = models.CharField(max_length=200, verbose_name="Nombre de la Unidad")
    link_unidad  = models.URLField(max_length=500, verbose_name="Link de la Unidad")

    def __str__(self):
        return f"{self.titulo} - {self.materia} (U.{self.unidad})"


class Colegio(models.Model):
    nombre    = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Colegio")
    ciudad    = models.CharField(max_length=100, verbose_name="Ciudad")
    mapa_link = models.URLField(blank=True, null=True, verbose_name="Link de Maps")

    def __str__(self):
        return self.nombre


class Profesor(models.Model):

    # ── Choices definidas dentro de la clase (convención Django moderna) ──
    class TipoCuenta(models.TextChoices):
        AHORROS   = 'Ahorros',   'Ahorros'
        CORRIENTE = 'Corriente', 'Corriente'

    class EstadoCivil(models.TextChoices):
        SOLTERO    = 'Soltero/a',    'Soltero/a'
        CASADO     = 'Casado/a',     'Casado/a'
        UNION      = 'Unión libre',  'Unión libre'
        DIVORCIADO = 'Divorciado/a', 'Divorciado/a'
        VIUDO      = 'Viudo/a',      'Viudo/a'

    class Banco(models.TextChoices):
        NEQUI      = 'Nequi',            'Nequi'
        BANCOLOMBIA = 'Bancolombia',     'Bancolombia'
        BOGOTA     = 'Banco de Bogotá',  'Banco de Bogotá'
        DAVIVIENDA = 'Davivienda',       'Davivienda'
        DAVIPLATA  = 'Daviplata',        'Daviplata'
        NU         = 'Nu',               'Nu'

    # ── Datos personales ──
    nombre           = models.CharField(max_length=200, verbose_name="Nombre(s)")
    apellido         = models.CharField(max_length=200, blank=True, null=True, verbose_name="Apellido(s)")
    documento        = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Cédula / Documento")
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    estado_civil     = models.CharField(
        max_length=20, blank=True, null=True,
        choices=EstadoCivil.choices, verbose_name="Estado Civil"
    )
    talla_camisa     = models.CharField(max_length=10, blank=True, null=True, verbose_name="Talla Camisa")

    # ── Contacto ──
    email     = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    celular   = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    ciudad    = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    direccion = models.CharField(max_length=300, blank=True, null=True, verbose_name="Dirección")

    # ── Información laboral ──
    area_materia  = models.CharField(max_length=200, blank=True, null=True, verbose_name="Área / Materia que dicta")
    disponibilidad = models.CharField(max_length=50, blank=True, null=True, verbose_name="Disponibilidad")
    eps           = models.CharField(max_length=100, blank=True, null=True, verbose_name="EPS")
    fondo_pension = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fondo de Pensión")

    # ── Datos bancarios ──
    banco           = models.CharField(
        max_length=100, blank=True, null=True,
        choices=Banco.choices, verbose_name="Banco"
    )
    tipo_cuenta     = models.CharField(
        max_length=20, blank=True, null=True,
        choices=TipoCuenta.choices, verbose_name="Tipo de Cuenta"
    )
    cuenta_bancaria = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cuenta Bancaria")

    @property
    def nombre_corto(self):
        primer_nombre   = self.nombre.split()[0] if self.nombre else ''
        primer_apellido = self.apellido.split()[0] if self.apellido else ''
        return f"{primer_nombre} {primer_apellido}".strip()

    def __str__(self):
        return self.nombre_corto