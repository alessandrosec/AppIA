# routes/auth_routes.py (actualizado)
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models.user import User
from models.audit_logs import AuditLog # Importa AuditLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.find_by_username(username)

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            AuditLog.log_action(user.id, user.username, 'LOGIN_SUCCESS', f'Inicio de sesión exitoso.', request.remote_addr)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            AuditLog.log_action(None, username, 'LOGIN_FAILED', f'Intento de inicio de sesión fallido con credenciales inválidas.', request.remote_addr)
            flash('Credenciales inválidas. Por favor, inténtalo de nuevo.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    AuditLog.log_action(current_user.id, current_user.username, 'LOGOUT', f'Cierre de sesión.', request.remote_addr)
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))