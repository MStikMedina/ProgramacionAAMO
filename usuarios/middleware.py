from django.shortcuts import redirect

# Rutas que no requieren autenticación
RUTAS_PUBLICAS = ['/usuarios/login/', '/usuarios/logout/', '/admin/']


class ControlAccesoMiddleware:
    """
    - Usuarios no autenticados → redirige al login.
    - Superusuarios → acceso total.
    - UsuarioColegio → solo /colegios/ con su colegio bloqueado.
    - UsuarioProfesor → solo /profesores/ con su profesor bloqueado.
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
            return self.get_response(request)

        # ── Usuario de Colegio ──────────────────────────────────────────────
        try:
            perfil = request.user.perfil_colegio
            # Adjuntar el perfil al request para que la vista lo use
            request.perfil_colegio  = perfil
            request.perfil_profesor = None
            # Solo puede acceder a /colegios/
            if not path.startswith('/colegios/'):
                return redirect(f'/colegios/?id_col={perfil.colegio.id}')
            return self.get_response(request)
        except Exception:
            pass

        # ── Usuario de Profesor ─────────────────────────────────────────────
        try:
            perfil = request.user.perfil_profesor
            request.perfil_colegio  = None
            request.perfil_profesor = perfil
            # Solo puede acceder a /profesores/
            if not path.startswith('/profesores/'):
                return redirect(f'/profesores/?profesor_id={perfil.profesor.id}')
            return self.get_response(request)
        except Exception:
            pass

        # Usuario autenticado sin perfil (no debería ocurrir, pero por seguridad)
        return self.get_response(request)