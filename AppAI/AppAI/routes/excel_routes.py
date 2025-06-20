# routes/excel_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash # Asegúrate de que 'request' esté aquí
from flask_login import login_required, current_user
from models.becario import Becario
from utils.decorators import role_required
from utils.excel_paser import parse_excel_to_becarios
from models.audit_logs import AuditLog # <--- Importa AuditLog
import os

excel_bp = Blueprint('excel', __name__, url_prefix='/excel')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@excel_bp.route('/cargar', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'asistente'])
def cargar_excel_becarios():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'EXCEL_UPLOAD_FAILED', 'Intento de carga de Excel sin archivo.', request.remote_addr)
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No se seleccionó ningún archivo.', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'EXCEL_UPLOAD_FAILED', 'Intento de carga de Excel con nombre de archivo vacío.', request.remote_addr)
            return redirect(request.url)

        if file and file.filename.endswith(('.xlsx', '.xls')):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            
            inserted_count = 0
            skipped_count = 0
            fraud_detections = []

            try:
                new_becarios_data, excel_fraud_detections = parse_excel_to_becarios(filepath)
                fraud_detections.extend(excel_fraud_detections) # Recolectar las detecciones del parser

                for becario_data in new_becarios_data:
                    existing_check = Becario.find_by_name_and_dob(
                        becario_data['nombres'], 
                        becario_data['apellidos'], 
                        becario_data['fecha_nacimiento']
                    )
                    
                    if existing_check and existing_check['es_ex_irsi']:
                        # Esta lógica ya se maneja en parse_excel_to_becarios, pero la mantenemos aquí por si acaso
                        flash(f"Se omitió a {becario_data['nombres']} {becario_data['apellidos']} (ya registrado como ex-IRSI en la DB).", 'warning')
                        skipped_count += 1
                        # Log de detección de fraude durante la inserción
                        AuditLog.log_action(current_user.id, current_user.username, 'FRAUD_DETECTED_EXCEL_INSERTION', 
                                            f'Becario del Excel ({becario_data["nombres"]} {becario_data["apellidos"]}) ya existe como ex-IRSI en DB (ID: {existing_check["id"]}). Omitido.', 
                                            request.remote_addr)
                        continue

                    if Becario.create(**becario_data):
                        inserted_count += 1
                        # Log de becario insertado desde Excel
                        AuditLog.log_action(current_user.id, current_user.username, 'EXCEL_BECARIO_INSERTED', 
                                            f'Becario insertado desde Excel: {becario_data["nombres"]} {becario_data["apellidos"]}.', 
                                            request.remote_addr)
                    else:
                        skipped_count += 1
                        flash(f"Error al importar el becario {becario_data['nombres']} {becario_data['apellidos']} (error de base de datos).", 'danger')
                        # Log de error al insertar becario desde Excel
                        AuditLog.log_action(current_user.id, current_user.username, 'EXCEL_BECARIO_INSERTION_FAILED', 
                                            f'Error al insertar becario desde Excel: {becario_data["nombres"]} {becario_data["apellidos"]}.', 
                                            request.remote_addr)

                # Log de resumen de la carga de Excel
                AuditLog.log_action(current_user.id, current_user.username, 'EXCEL_UPLOAD_SUMMARY', 
                                    f'Carga de Excel "{file.filename}" finalizada. Insertados: {inserted_count}, Omitidos: {skipped_count}. Detecciones de fraude: {len(fraud_detections)}.', 
                                    request.remote_addr)
                
                flash(f'Importación finalizada. Se insertaron {inserted_count} becarios nuevos. Se omitieron {skipped_count} (duplicados o errores).', 'success')

                if fraud_detections:
                    flash('¡Alertas de posible fraude o ex-IRSI detectados en el archivo Excel! Revisa los detalles.', 'warning')
                    # Ya se hizo el log individual para cada detección en excel_parser, pero aquí se puede reforzar o dar un resumen.
                    # El re-renderizado de la plantilla mostrará los detalles.
            except Exception as e:
                flash(f'Error al procesar el archivo Excel: {str(e)}', 'danger')
                # Log de error grave en el procesamiento del Excel
                AuditLog.log_action(current_user.id, current_user.username, 'EXCEL_PROCESS_ERROR', 
                                    f'Error crítico al procesar el archivo Excel "{file.filename}": {str(e)}.', 
                                    request.remote_addr)
            finally:
                if os.path.exists(filepath): # Asegurarse de que el archivo existe antes de intentar eliminarlo
                    os.remove(filepath)
        else:
            flash('Tipo de archivo no permitido. Por favor, sube un archivo .xlsx o .xls', 'danger')
            AuditLog.log_action(current_user.id, current_user.username, 'EXCEL_UPLOAD_FAILED', 
                                f'Intento de carga de Excel con tipo de archivo no permitido: {file.filename}.', 
                                request.remote_addr)

    return render_template('excel/cargar.html', fraud_detections=fraud_detections if 'fraud_detections' in locals() else [])