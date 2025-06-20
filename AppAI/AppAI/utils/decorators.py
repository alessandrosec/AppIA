from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def role_required(roles):
    """
    Decorador para restringir el acceso a rutas basadas en el rol del usuario actual.
    :param roles: Una lista de roles permitidos (ej. ['admin', 'asistente']).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('No tienes permiso para acceder a esta página.', 'danger')
                abort(403) # Error 403 Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator