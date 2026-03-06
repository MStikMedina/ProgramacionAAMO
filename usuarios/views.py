from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import UsuarioColegio, UsuarioProfesor
from configuracion.models import Colegio, Profesor


# ── Helpers ──────────────────────────────────────────────────────────────────

def solo_admin(user):
    return user.is_superuser


def login_redirect(request):
    """Redirige al usuario al área correcta según su tipo."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        return redirect('home')
    try:
        perfil = request.user.perfil_colegio
        return redirect(f'/colegios/?id_col={perfil.colegio.id}')
    except UsuarioColegio.DoesNotExist:
        pass
    try:
        perfil = request.user.perfil_profesor
        return redirect(f'/profesores/?profesor_id={perfil.profesor.id}')
    except UsuarioProfesor.DoesNotExist:
        pass
    return redirect('home')


# ── Login / Logout ────────────────────────────────────────────────────────────

def vista_login(request):
    if request.user.is_authenticated:
        return login_redirect(request)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return login_redirect(request)
        else:
            error = 'Usuario o contraseña incorrectos.'

    return render(request, 'usuarios/login.html', {'error': error})


def vista_logout(request):
    logout(request)
    return redirect('login')


# ── Gestión de usuarios (solo admin) ─────────────────────────────────────────

@user_passes_test(solo_admin, login_url='login')
def gestionar_usuarios(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')

        # ── Crear usuario colegio ──
        if accion == 'crear_colegio':
            username   = request.POST.get('username', '').strip()
            password   = request.POST.get('password', '').strip()
            colegio_id = request.POST.get('colegio_id')
            if not username or not password or not colegio_id:
                messages.error(request, 'Completa todos los campos.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, f'El usuario "{username}" ya existe.')
            else:
                user = User.objects.create_user(username=username, password=password,
                                                 is_staff=False, is_superuser=False)
                colegio = get_object_or_404(Colegio, id=colegio_id)
                UsuarioColegio.objects.create(user=user, colegio=colegio, password_texto=password)
                messages.success(request, f'Usuario "{username}" creado para {colegio.nombre}.')

        # ── Crear usuario profesor ──
        elif accion == 'crear_profesor':
            username    = request.POST.get('username', '').strip()
            password    = request.POST.get('password', '').strip()
            profesor_id = request.POST.get('profesor_id')
            if not username or not password or not profesor_id:
                messages.error(request, 'Completa todos los campos.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, f'El usuario "{username}" ya existe.')
            else:
                user = User.objects.create_user(username=username, password=password,
                                                 is_staff=False, is_superuser=False)
                profesor = get_object_or_404(Profesor, id=profesor_id)
                UsuarioProfesor.objects.create(user=user, profesor=profesor, password_texto=password)
                messages.success(request, f'Usuario "{username}" creado para {profesor.nombre}.')

        # ── Editar usuario colegio ──
        elif accion == 'editar_colegio':
            perfil_id    = request.POST.get('perfil_id')
            new_username = request.POST.get('username', '').strip()
            new_password = request.POST.get('password', '').strip()
            new_col_id   = request.POST.get('colegio_id')
            perfil = get_object_or_404(UsuarioColegio, id=perfil_id)

            if new_username != perfil.user.username:
                if User.objects.filter(username=new_username).exclude(id=perfil.user.id).exists():
                    messages.error(request, f'El usuario "{new_username}" ya existe.')
                    return redirect('gestionar_usuarios')
                perfil.user.username = new_username

            if new_password:
                perfil.user.set_password(new_password)
                perfil.password_texto = new_password

            perfil.user.save()
            perfil.colegio = get_object_or_404(Colegio, id=new_col_id)
            perfil.save()
            messages.success(request, 'Usuario de colegio actualizado.')

        # ── Editar usuario profesor ──
        elif accion == 'editar_profesor':
            perfil_id    = request.POST.get('perfil_id')
            new_username = request.POST.get('username', '').strip()
            new_password = request.POST.get('password', '').strip()
            new_prof_id  = request.POST.get('profesor_id')
            perfil = get_object_or_404(UsuarioProfesor, id=perfil_id)

            if new_username != perfil.user.username:
                if User.objects.filter(username=new_username).exclude(id=perfil.user.id).exclude(id=perfil.user.id).exists():
                    messages.error(request, f'El usuario "{new_username}" ya existe.')
                    return redirect('gestionar_usuarios')
                perfil.user.username = new_username

            if new_password:
                perfil.user.set_password(new_password)
                perfil.password_texto = new_password

            perfil.user.save()
            perfil.profesor = get_object_or_404(Profesor, id=new_prof_id)
            perfil.save()
            messages.success(request, 'Usuario de profesor actualizado.')

        # ── Eliminar usuario colegio ──
        elif accion == 'eliminar_colegio':
            perfil = get_object_or_404(UsuarioColegio, id=request.POST.get('perfil_id'))
            nombre = perfil.user.username
            perfil.user.delete()
            messages.success(request, f'Usuario "{nombre}" eliminado.')

        # ── Eliminar usuario profesor ──
        elif accion == 'eliminar_profesor':
            perfil = get_object_or_404(UsuarioProfesor, id=request.POST.get('perfil_id'))
            nombre = perfil.user.username
            perfil.user.delete()
            messages.success(request, f'Usuario "{nombre}" eliminado.')

        return redirect('gestionar_usuarios')

    # GET
    usuarios_colegio  = UsuarioColegio.objects.select_related('user', 'colegio').order_by('colegio__nombre', 'user__username')
    usuarios_profesor = UsuarioProfesor.objects.select_related('user', 'profesor').order_by('profesor__nombre', 'user__username')
    colegios  = Colegio.objects.all().order_by('nombre')
    profesores = Profesor.objects.all().order_by('nombre')

    return render(request, 'usuarios/gestionar.html', {
        'usuarios_colegio':  usuarios_colegio,
        'usuarios_profesor': usuarios_profesor,
        'colegios':  colegios,
        'profesores': profesores,
    })