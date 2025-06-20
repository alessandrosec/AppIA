# routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort # Asegúrate de que 'request' esté aquí
from flask_login import login_required, current_user
from models.user import User
from models.becario import Becario
from utils.decorators import role_required
from models.audit_logs import AuditLog # <--- Importa AuditLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ROLES_PERMITIDOS = ['admin', 'asistente', 'director', 'consulta']

@admin_bp.route('/users')
@login_required
@role_required(['admin'])
def lista_usuarios():
    # Log de vista de lista de usuarios
    AuditLog.log_action(current_user.id, current_user.username, 'VIEW_USER_LIST', f'Lista de usuarios vista por {current_user.username}.', request.remote_addr)
    users = User.get_all_users()
    return render_template('admin/lista_usuarios.html', users=users, roles_permitidos=ROLES_PERMITIDOS)

@admin_bp.route('/audit_logs')
@login_required
@role_required(['admin'])
def view_audit_logs():
    logs = AuditLog.get_all_logs()
    # Opcional: Loggear la vista de logs, aunque ya estamos en el módulo de auditoría.
    AuditLog.log_action(current_user.id, current_user.username, 'VIEW_AUDIT_LOGS', 'Visualización de logs de auditoría.', request.remote_addr)
    return render_template('admin/audit_logs.html', logs=logs)

@admin_bp.route('/reports')
@login_required
@role_required(['admin', 'director']) # Admin y Director pueden ver reportes
def system_reports():
    total_becarios = Becario.count_total_becarios()
    ex_irsi_becarios = Becario.count_ex_irsi_becarios()
    becarios_by_nationality = Becario.count_becarios_by_nationality()

    total_users = User.count_total_users()
    users_by_role = User.count_users_by_role()

    # Log de vista de reportes
    AuditLog.log_action(current_user.id, current_user.username, 'VIEW_SYSTEM_REPORTS', 'Visualización de reportes del sistema.', request.remote_addr)

    return render_template('admin/system_reports.html',
                           total_becarios=total_becarios,
                           ex_irsi_becarios=ex_irsi_becarios,
                           becarios_by_nationality=becarios_by_nationality,
                           total_users=total_users,
                           users_by_role=users_by_role)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def crear_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if not (username and password and confirm_password and role):
            flash('Todos los campos son obligatorios.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_USER_FAILED', f'Intento fallido de crear usuario (campos incompletos).', request.remote_addr)
            return render_template('admin/crear_usuario.html', roles_permitidos=ROLES_PERMITIDOS)

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_USER_FAILED', f'Intento fallido de crear usuario {username} (contraseñas no coinciden).', request.remote_addr)
            return render_template('admin/crear_usuario.html', roles_permitidos=ROLES_PERMITIDOS)
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_USER_FAILED', f'Intento fallido de crear usuario {username} (contraseña débil).', request.remote_addr)
            return render_template('admin/crear_usuario.html', roles_permitidos=ROLES_PERMITIDOS)

        if role not in ROLES_PERMITIDOS:
            flash('Rol no válido.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_USER_FAILED', f'Intento fallido de crear usuario {username} (rol inválido: {role}).', request.remote_addr)
            return render_template('admin/crear_usuario.html', roles_permitidos=ROLES_PERMITIDOS)

        if User.find_by_username(username):
            flash(f'El usuario "{username}" ya existe.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_USER_FAILED', f'Intento fallido de crear usuario {username} (usuario ya existe).', request.remote_addr)
            return render_template('admin/crear_usuario.html', roles_permitidos=ROLES_PERMITIDOS, form_data=request.form)

        if User.create_user(username, password, role):
            # Log de creación de usuario exitosa
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_USER_SUCCESS', f'Usuario "{username}" con rol "{role}" creado exitosamente.', request.remote_addr)
            flash(f'Usuario "{username}" creado exitosamente.', 'success')
            return redirect(url_for('admin.lista_usuarios'))
        else:
            # Log de error general al crear usuario
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_USER_FAILED', f'Error inesperado al crear el usuario "{username}".', request.remote_addr)
            flash('Error al crear el usuario. Inténtalo de nuevo.', 'danger')

    return render_template('admin/crear_usuario.html', roles_permitidos=ROLES_PERMITIDOS)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def editar_usuario(user_id):
    user = User.get(user_id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        AuditLog.log_action(current_user.id, current_user.username, 'EDIT_USER_FAILED', f'Intento de editar usuario no existente: ID {user_id}.', request.remote_addr)
        return redirect(url_for('admin.lista_usuarios'))

    if request.method == 'POST':
        old_username = user.username # Guardar para el log
        
        username = request.form['username']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']
        role = request.form['role']

        if not (username and role):
            flash('Usuario y rol son obligatorios.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_USER_FAILED', f'Intento fallido de actualizar usuario {old_username} (campos incompletos).', request.remote_addr)
            return render_template('admin/editar_usuario.html', user=user, roles_permitidos=ROLES_PERMITIDOS)
            
        if role not in ROLES_PERMITIDOS:
            flash('Rol no válido.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_USER_FAILED', f'Intento fallido de actualizar usuario {old_username} (rol inválido: {role}).', request.remote_addr)
            return render_template('admin/editar_usuario.html', user=user, roles_permitidos=ROLES_PERMITIDOS)

        if new_password:
            if new_password != confirm_new_password:
                flash('Las nuevas contraseñas no coinciden.', 'danger')
                AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_USER_FAILED', f'Intento fallido de actualizar contraseña para {old_username} (contraseñas no coinciden).', request.remote_addr)
                return render_template('admin/editar_usuario.html', user=user, roles_permitidos=ROLES_PERMITIDOS)
            if len(new_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
                AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_USER_FAILED', f'Intento fallido de actualizar contraseña para {old_username} (contraseña débil).', request.remote_addr)
                return render_template('admin/editar_usuario.html', user=user, roles_permitidos=ROLES_PERMITIDOS)
        
        existing_user_with_username = User.find_by_username(username)
        if existing_user_with_username and existing_user_with_username.id != user_id:
            flash(f'El nombre de usuario "{username}" ya está en uso por otro usuario.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_USER_FAILED', f'Intento fallido de actualizar usuario {old_username} a {username} (nombre de usuario ya en uso).', request.remote_addr)
            return render_template('admin/editar_usuario.html', user=user, roles_permitidos=ROLES_PERMITIDOS)

        if User.update_user(user_id, username, role, new_password):
            # Log de actualización de usuario exitosa
            AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_USER_SUCCESS', f'Usuario actualizado: {old_username} (ID: {user_id}) a {username} con rol {role}.', request.remote_addr)
            flash(f'Usuario "{username}" actualizado exitosamente.', 'success')
            return redirect(url_for('admin.lista_usuarios'))
        else:
            # Log de error general al actualizar usuario
            AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_USER_FAILED', f'Error inesperado al actualizar el usuario "{old_username}" (ID: {user_id}).', request.remote_addr)
            flash('Error al actualizar el usuario. Inténtalo de nuevo.', 'danger')

    return render_template('admin/editar_usuario.html', user=user, roles_permitidos=ROLES_PERMITIDOS)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def eliminar_usuario(user_id):
    if current_user.id == user_id:
        flash('No puedes eliminar tu propia cuenta de administrador.', 'danger')
        AuditLog.log_action(current_user.id, current_user.username, 'DELETE_USER_FAILED', f'Intento de auto-eliminación de cuenta.', request.remote_addr)
        return redirect(url_for('admin.lista_usuarios'))

    user_to_delete = User.get(user_id) # Obtener el usuario antes de eliminar para el log
    if not user_to_delete:
        flash('Usuario no encontrado para eliminar.', 'danger')
        AuditLog.log_action(current_user.id, current_user.username, 'DELETE_USER_FAILED', f'Intento de eliminar usuario no existente: ID {user_id}.', request.remote_addr)
        return redirect(url_for('admin.lista_usuarios'))

    if User.delete_user(user_id):
        # Log de eliminación de usuario exitosa
        AuditLog.log_action(current_user.id, current_user.username, 'DELETE_USER_SUCCESS', f'Usuario eliminado: {user_to_delete.username} (ID: {user_id}).', request.remote_addr)
        flash('Usuario eliminado exitosamente.', 'success')
    else:
        # Log de error al eliminar usuario
        AuditLog.log_action(current_user.id, current_user.username, 'DELETE_USER_FAILED', f'Error al eliminar usuario: {user_to_delete.username} (ID: {user_id}).', request.remote_addr)
        flash('Error al eliminar el usuario.', 'danger')
    return redirect(url_for('admin.lista_usuarios'))