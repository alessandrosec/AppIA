import openpyxl
from datetime import datetime
from models.becario import Becario
# from models.audit_log import AuditLog # <--- No se importa aquí, se envía a excel_routes para loguear

# Formato de columnas esperado en el Excel
EXCEL_COLUMNS = {
    'NOMBRES': 0,
    'APELLIDOS': 1,
    'TITULO': 2,
    'FECHA_NACIMIENTO': 3,
    'CORREO_PERSONAL': 4,
    'CORREO_INSTITUCIONAL': 5,
    'TELEFONO': 6,
    'DIRECCION': 7,
    'PAIS_ORIGEN': 8,
    'NACIONALIDAD': 9,
    'HISTORIAL_CIBERSEGURIDAD': 10,
    'ES_EX_IRSI': 11,
    'FECHA_INGRESO_IRSI': 12
}

def parse_excel_to_becarios(filepath):
    """
    Parsea un archivo Excel y devuelve una lista de diccionarios de becarios
    listos para ser insertados, y una lista de detecciones de fraude/ex-IRSI.
    """
    workbook = openpyxl.load_workbook(filepath)
    sheet = workbook.active
    
    becarios_to_insert = []
    fraud_detections = [] # Guardará información de los becarios que ya existen o son ex-IRSI

    for row_idx in range(2, sheet.max_row + 1):
        try:
            row_data = [cell.value for cell in sheet[row_idx]]

            nombres = str(row_data[EXCEL_COLUMNS['NOMBRES']]).strip() if row_data[EXCEL_COLUMNS['NOMBRES']] else None
            apellidos = str(row_data[EXCEL_COLUMNS['APELLIDOS']]).strip() if row_data[EXCEL_COLUMNS['APELLIDOS']] else None
            
            fecha_nacimiento_raw = row_data[EXCEL_COLUMNS['FECHA_NACIMIENTO']]
            fecha_nacimiento = None
            if fecha_nacimiento_raw:
                if isinstance(fecha_nacimiento_raw, datetime):
                    fecha_nacimiento = fecha_nacimiento_raw.date()
                elif isinstance(fecha_nacimiento_raw, str):
                    try:
                        fecha_nacimiento = datetime.strptime(fecha_nacimiento_raw, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            fecha_nacimiento = datetime.strptime(fecha_nacimiento_raw, '%d/%m/%Y').date()
                        except ValueError:
                            print(f"Advertencia (parser): Fecha de nacimiento inválida para {nombres} {apellidos} en fila {row_idx}: {fecha_nacimiento_raw}")
                            fecha_nacimiento = None

            if not (nombres and apellidos and fecha_nacimiento):
                print(f"Saltando fila {row_idx}: Datos básicos (nombre, apellido, fecha_nacimiento) incompletos.")
                # Se podría agregar al fraud_detections con motivo 'datos_incompletos' si se desea reportar
                continue

            existing_becario = Becario.find_by_name_and_dob(nombres, apellidos, fecha_nacimiento)

            if existing_becario:
                detection_info = {
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'fecha_nacimiento': fecha_nacimiento.strftime('%Y-%m-%d'),
                    'es_ex_irsi_db': existing_becario['es_ex_irsi'],
                    'id_db': existing_becario['id'],
                    'motivo': 'Ya registrado y/o ex-IRSI'
                }
                fraud_detections.append(detection_info)
                # No se loguea aquí directamente para evitar dependencias circulares y centralizar el loggeo en la ruta.
                # La ruta de excel_routes.py se encargará de loguear estas detecciones.
                continue

            es_ex_irsi_raw = str(row_data[EXCEL_COLUMNS['ES_EX_IRSI']]).strip().lower() if row_data[EXCEL_COLUMNS['ES_EX_IRSI']] else '0'
            es_ex_irsi = es_ex_irsi_raw in ['1', 'true', 'sí', 'si', 'yes']

            fecha_ingreso_irsi_raw = row_data[EXCEL_COLUMNS['FECHA_INGRESO_IRSI']] # <-- Corregido el nombre de la columna aquí
            fecha_ingreso_irsi = None
            if fecha_ingreso_irsi_raw:
                if isinstance(fecha_ingreso_irsi_raw, datetime):
                    fecha_ingreso_irsi = fecha_ingreso_irsi_raw.date()
                elif isinstance(fecha_ingreso_irsi_raw, str):
                    try:
                        fecha_ingreso_irsi = datetime.strptime(fecha_ingreso_irsi_raw, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            fecha_ingreso_irsi = datetime.strptime(fecha_ingreso_irsi_raw, '%d/%m/%Y').date()
                        except ValueError:
                            print(f"Advertencia (parser): Fecha de ingreso IRSI inválida para {nombres} {apellidos} en fila {row_idx}: {fecha_ingreso_irsi_raw}")
                            fecha_ingreso_irsi = None

            becario_data = {
                'id': None,
                'nombres': nombres,
                'apellidos': apellidos,
                'titulo': str(row_data[EXCEL_COLUMNS['TITULO']]).strip() if row_data[EXCEL_COLUMNS['TITULO']] else None,
                'fecha_nacimiento': fecha_nacimiento,
                'correo_personal': str(row_data[EXCEL_COLUMNS['CORREO_PERSONAL']]).strip() if row_data[EXCEL_COLUMNS['CORREO_PERSONAL']] else None,
                'correo_institucional': str(row_data[EXCEL_COLUMNS['CORREO_INSTITUCIONAL']]).strip() if row_data[EXCEL_COLUMNS['CORREO_INSTITUCIONAL']] else None,
                'telefono': str(row_data[EXCEL_COLUMNS['TELEFONO']]).strip() if row_data[EXCEL_COLUMNS['TELEFONO']] else None,
                'direccion': str(row_data[EXCEL_COLUMNS['DIRECCION']]).strip() if row_data[EXCEL_COLUMNS['DIRECCION']] else None,
                'pais_origen': str(row_data[EXCEL_COLUMNS['PAIS_ORIGEN']]).strip() if row_data[EXCEL_COLUMNS['PAIS_ORIGEN']] else None,
                'nacionalidad': str(row_data[EXCEL_COLUMNS['NACIONALIDAD']]).strip() if row_data[EXCEL_COLUMNS['NACIONALIDAD']] else None,
                'historial_ciberseguridad': str(row_data[EXCEL_COLUMNS['HISTORIAL_CIBERSEGURIDAD']]).strip() if row_data[EXCEL_COLUMNS['HISTORIAL_CIBERSEGURIDAD']] else None,
                'es_ex_irsi': es_ex_irsi,
                'fecha_ingreso_irsi': fecha_ingreso_irsi
            }
            becarios_to_insert.append(becario_data)

        except Exception as e:
            print(f"Error procesando la fila {row_idx} en el parser: {e}")
            # Se podría añadir un log aquí si se desea tener un registro de errores de parsing más granular.
            # Por ahora, el error se imprime y se captura en la ruta principal.
            pass

    return becarios_to_insert, fraud_detections