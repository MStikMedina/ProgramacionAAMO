from django.shortcuts import redirect
from django.http import HttpResponseForbidden

# Rutas que no requieren autenticación
RUTAS_PUBLICAS = ['/usuarios/login/', '/usuarios/logout/', '/admin/']


class ControlAccesoMiddleware:
    """
    Niveles de acceso:
    - No autenticado        → solo login
    - Superusuario          → acceso total
    - UsuarioColegio        → solo /colegios/ y únicamente con su colegio (id forzado en la vista)
    - UsuarioProfesor       → solo /profesores/ y únicamente con su profesor (id forzado en la vista)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Siempre permitir rutas públicas y archivos estáticos
        if (any(path.startswith(r) for r in RUTAS_PUBLICAS)
                or path.startswith('/static/')
                or path.startswith('/media/')):
            return self.get_response(request)

        # Redirigir al login si no está autenticado
        if not request.user.is_authenticated:
            return redirect(f'/usuarios/login/?next={path}')

        # Superusuario: acceso total
        if request.user.is_superuser:
            request.perfil_colegio  = None
            request.perfil_profesor = None
            return self.get_response(request)

        # ── Usuario de Colegio ──────────────────────────────────────────────
        try:
            perfil = request.user.perfil_colegio
            request.perfil_colegio  = perfil
            request.perfil_profesor = None

            # Rutas permitidas para usuario de colegio
            PERMITIDAS_COLEGIO = ['/colegios/']
            if not any(path.startswith(r) for r in PERMITIDAS_COLEGIO):
                # Cualquier otra ruta → devolver al su colegio
                return redirect(f'/colegios/?id_col={perfil.colegio.id}')

            return self.get_response(request)
        except Exception:
            pass

        # ── Usuario de Profesor ─────────────────────────────────────────────
        try:
            perfil = request.user.perfil_profesor
            request.perfil_colegio  = None
            request.perfil_profesor = perfil

            # Rutas permitidas para usuario de profesor
            PERMITIDAS_PROFESOR = ['/profesores/']
            if not any(path.startswith(r) for r in PERMITIDAS_PROFESOR):
                # Cualquier otra ruta → devolver a su horario
                return redirect(f'/profesores/?profesor_id={perfil.profesor.id}')

            return self.get_response(request)
        except Exception:
            pass

        # Usuario autenticado sin perfil asignado → logout forzado
        from django.contrib.auth import logout
        logout(request)
        return redirect('/usuarios/login/')