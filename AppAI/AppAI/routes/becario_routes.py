# routes/becario_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash # Asegúrate de que 'request' esté aquí
from flask_login import login_required, current_user
from models.becario import Becario
from utils.decorators import role_required
from models.audit_logs import AuditLog # <--- Importa AuditLog

becario_bp = Blueprint('becario', __name__, url_prefix='/becarios')

@becario_bp.route('/')
@login_required
@role_required(['admin', 'asistente', 'director', 'consulta'])
def lista_becarios():
    # No es necesario loggear cada vista de lista, a menos que sea crítico
    becarios = Becario.get_all()
    return render_template('becarios/lista.html', becarios=becarios)

@becario_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'asistente'])
def crear_becario():
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        titulo = request.form.get('titulo')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        correo_personal = request.form.get('correo_personal')
        correo_institucional = request.form.get('correo_institucional')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        pais_origen = request.form.get('pais_origen')
        nacionalidad = request.form.get('nacionalidad')
        historial_ciberseguridad = request.form.get('historial_ciberseguridad')
        es_ex_irsi = bool(request.form.get('es_ex_irsi'))
        fecha_ingreso_irsi = request.form.get('fecha_ingreso_irsi')

        existing_becario = Becario.find_by_name_and_dob(nombres, apellidos, fecha_nacimiento)
        if existing_becario:
            flash(f'¡Alerta de Fraude! Ya existe un becario con ese nombre ({nombres} {apellidos}) y fecha de nacimiento ({fecha_nacimiento}). Es un ex-IRSI: {existing_becario["es_ex_irsi"]}', 'danger')
            # Log de intento de creación de becario duplicado/fraude
            AuditLog.log_action(current_user.id, current_user.username, 'FRAUD_DETECTION_CREATE_BECARIO', f'Intento de crear becario duplicado: {nombres} {apellidos} (Ya existe ID: {existing_becario["id"]}).', request.remote_addr)
            return render_template('becarios/crear.html', form_data=request.form)

        if Becario.create(nombres, apellidos, titulo, fecha_nacimiento,
                         correo_personal, correo_institucional, telefono, direccion,
                         pais_origen, nacionalidad, historial_ciberseguridad,
                         es_ex_irsi, fecha_ingreso_irsi):
            # Log de creación de becario exitosa
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_BECARIO_SUCCESS', f'Becario creado: {nombres} {apellidos}.', request.remote_addr)
            flash('Becario creado exitosamente.', 'success')
            return redirect(url_for('becario.lista_becarios'))
        else:
            # Log de error al crear becario
            AuditLog.log_action(current_user.id, current_user.username, 'CREATE_BECARIO_FAILED', f'Error al crear becario: {nombres} {apellidos}.', request.remote_addr)
            flash('Error al crear el becario. Por favor, verifica los datos.', 'danger')

    return render_template('becarios/crear.html')

@becario_bp.route('/detalle/<int:becario_id>')
@login_required
@role_required(['admin', 'asistente', 'director', 'consulta'])
def detalle_becario(becario_id):
    becario = Becario.get_by_id(becario_id)
    if not becario:
        flash('Becario no encontrado.', 'danger')
        # AuditLog.log_action(current_user.id, current_user.username, 'VIEW_BECARIO_NOT_FOUND', f'Intento de ver detalle de becario no existente: ID {becario_id}.', request.remote_addr) # Opcional: loggear no encontrados
        return redirect(url_for('becario.lista_becarios'))
    # Log de vista de detalle de becario
    AuditLog.log_action(current_user.id, current_user.username, 'VIEW_BECARIO_DETAIL', f'Detalle de becario visto: {becario.nombres} {becario.apellidos} (ID: {becario_id}).', request.remote_addr)
    return render_template('becarios/detalle.html', becario=becario)

@becario_bp.route('/editar/<int:becario_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'asistente'])
def editar_becario(becario_id):
    becario = Becario.get_by_id(becario_id)
    if not becario:
        flash('Becario no encontrado.', 'danger')
        # AuditLog.log_action(current_user.id, current_user.username, 'EDIT_BECARIO_NOT_FOUND', f'Intento de editar becario no existente: ID {becario_id}.', request.remote_addr) # Opcional: loggear no encontrados
        return redirect(url_for('becario.lista_becarios'))

    if request.method == 'POST':
        old_nombres = becario.nombres # Guarda el nombre anterior para el log
        old_apellidos = becario.apellidos # Guarda el apellido anterior para el log

        becario.nombres = request.form['nombres']
        becario.apellidos = request.form['apellidos']
        becario.titulo = request.form.get('titulo')
        becario.fecha_nacimiento = request.form.get('fecha_nacimiento')
        becario.correo_personal = request.form.get('correo_personal')
        becario.correo_institucional = request.form.get('correo_institucional')
        becario.telefono = request.form.get('telefono')
        becario.direccion = request.form.get('direccion')
        becario.pais_origen = request.form.get('pais_origen')
        becario.nacionalidad = request.form.get('nacionalidad')
        becario.historial_ciberseguridad = request.form.get('historial_ciberseguridad')
        becario.es_ex_irsi = bool(request.form.get('es_ex_irsi'))
        becario.fecha_ingreso_irsi = request.form.get('fecha_ingreso_irsi')

        if Becario.update(becario):
            # Log de actualización de becario exitosa
            AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_BECARIO_SUCCESS', f'Becario actualizado: {old_nombres} {old_apellidos} (ID: {becario.id}) a {becario.nombres} {becario.apellidos}.', request.remote_addr)
            flash('Becario actualizado exitosamente.', 'success')
            return redirect(url_for('becario.detalle_becario', becario_id=becario.id))
        else:
            # Log de error al actualizar becario
            AuditLog.log_action(current_user.id, current_user.username, 'UPDATE_BECARIO_FAILED', f'Error al actualizar becario: {old_nombres} {old_apellidos} (ID: {becario.id}).', request.remote_addr)
            flash('Error al actualizar el becario.', 'danger')
    return render_template('becarios/editar.html', becario=becario)

@becario_bp.route('/eliminar/<int:becario_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def eliminar_becario(becario_id):
    becario = Becario.get_by_id(becario_id) # Obtener el becario antes de eliminar para el log
    if not becario:
        flash('Becario no encontrado para eliminar.', 'danger')
        AuditLog.log_action(current_user.id, current_user.username, 'DELETE_BECARIO_FAILED', f'Intento de eliminar becario no existente: ID {becario_id}.', request.remote_addr)
        return redirect(url_for('becario.lista_becarios'))

    if Becario.delete(becario_id):
        # Log de eliminación de becario exitosa
        AuditLog.log_action(current_user.id, current_user.username, 'DELETE_BECARIO_SUCCESS', f'Becario eliminado: {becario.nombres} {becario.apellidos} (ID: {becario_id}).', request.remote_addr)
        flash('Becario eliminado exitosamente.', 'success')
    else:
        # Log de error al eliminar becario
        AuditLog.log_action(current_user.id, current_user.username, 'DELETE_BECARIO_FAILED', f'Error al eliminar becario: {becario.nombres} {becario.apellidos} (ID: {becario_id}).', request.remote_addr)
        flash('Error al eliminar el becario.', 'danger')
    return redirect(url_for('becario.lista_becarios'))