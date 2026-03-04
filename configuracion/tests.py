from django.test import TestCase
from .models import Libro, Colegio, Profesor


class ProfesorNombreCortoTest(TestCase):
    """Prueba que nombre_corto devuelva siempre el formato correcto."""

    def test_nombre_corto_con_nombre_y_apellido(self):
        p = Profesor(nombre='Juan Carlos', apellido='García López')
        self.assertEqual(p.nombre_corto, 'Juan García')

    def test_nombre_corto_sin_apellido(self):
        # Profesor sin apellido cargado aún
        p = Profesor(nombre='Mariela', apellido=None)
        self.assertEqual(p.nombre_corto, 'Mariela')

    def test_nombre_corto_sin_nombre(self):
        # Caso extremo: nombre vacío
        p = Profesor(nombre='', apellido='García')
        self.assertEqual(p.nombre_corto, 'García')

    def test_str_devuelve_nombre_corto(self):
        p = Profesor(nombre='Waldo', apellido='Guerra Blanco')
        self.assertEqual(str(p), 'Waldo Guerra')


class LibroStrTest(TestCase):
    """Prueba que __str__ del libro devuelva el formato esperado."""

    def test_str_libro(self):
        lib = Libro(titulo='Saberes 11', materia='Matemáticas', unidad='3',
                    nombre_unidad='Funciones', link_unidad='https://ejemplo.com')
        self.assertEqual(str(lib), 'Saberes 11 - Matemáticas (U.3)')


class ColegioStrTest(TestCase):
    """Prueba que __str__ del colegio devuelva el nombre."""

    def test_str_colegio(self):
        c = Colegio(nombre='Pablo Hoff Cartagena', ciudad='Cartagena')
        self.assertEqual(str(c), 'Pablo Hoff Cartagena')