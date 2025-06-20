import pyodbc
from config import Config
from datetime import date # Para manejar fechas

class Becario:
    def __init__(self, id, nombres, apellidos, titulo, fecha_nacimiento,
                 correo_personal, correo_institucional, telefono, direccion,
                 pais_origen, nacionalidad, historial_ciberseguridad,
                 es_ex_irsi, fecha_ingreso_irsi=None):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.titulo = titulo
        self.fecha_nacimiento = fecha_nacimiento if isinstance(fecha_nacimiento, date) else self._convert_to_date(fecha_nacimiento)
        self.correo_personal = correo_personal
        self.correo_institucional = correo_institucional
        self.telefono = telefono
        self.direccion = direccion
        self.pais_origen = pais_origen
        self.nacionalidad = nacionalidad
        self.historial_ciberseguridad = historial_ciberseguridad
        self.es_ex_irsi = bool(es_ex_irsi) # Asegurar que sea booleano
        self.fecha_ingreso_irsi = fecha_ingreso_irsi if isinstance(fecha_ingreso_irsi, date) or fecha_ingreso_irsi is None else self._convert_to_date(fecha_ingreso_irsi)

    def _convert_to_date(self, date_str):
        if date_str:
            try:
                # Intenta convertir de string (YYYY-MM-DD) a objeto date
                return date.fromisoformat(date_str)
            except ValueError:
                return None # O manejar el error de forma más robusta
        return None

    @staticmethod
    def create(nombres, apellidos, titulo, fecha_nacimiento,
                 correo_personal, correo_institucional, telefono, direccion,
                 pais_origen, nacionalidad, historial_ciberseguridad,
                 es_ex_irsi, fecha_ingreso_irsi=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Becarios (Nombres, Apellidos, Titulo, FechaNacimiento,
                                      CorreoPersonal, CorreoInstitucional, Telefono, Direccion,
                                      PaisOrigen, Nacionalidad, HistorialCiberseguridad,
                                      EsExIRSI, FechaIngresoIRSI)
                OUTPUT INSERTED.id -- Para obtener el ID del nuevo registro
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                nombres, apellidos, Becario._safestr(titulo), Becario._safe_date(fecha_nacimiento),
                Becario._safestr(correo_personal), Becario._safestr(correo_institucional), Becario._safestr(telefono), Becario._safestr(direccion),
                Becario._safestr(pais_origen), Becario._safestr(nacionalidad), Becario._safestr(historial_ciberseguridad),
                bool(es_ex_irsi), Becario._safe_date(fecha_ingreso_irsi)
            )
            new_id = cursor.fetchone()[0] # Obtiene el ID insertado
            conn.commit()
            return True # O podrías devolver la instancia del nuevo Becario(new_id, ...)
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al crear becario: {sqlstate} - {ex}")
            conn.rollback() # Deshacer si hay error
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all():
        conn = None
        cursor = None
        becarios = []
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Becarios ORDER BY Nombres, Apellidos")
            for row in cursor.fetchall():
                becarios.append(Becario(*row)) # Desempaqueta la tupla directamente
            return becarios
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al obtener becarios: {sqlstate} - {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_id(becario_id):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Becarios WHERE id = ?", becario_id)
            row = cursor.fetchone()
            if row:
                return Becario(*row)
            return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al obtener becario por ID: {sqlstate} - {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update(becario):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE Becarios
                SET Nombres = ?, Apellidos = ?, Titulo = ?, FechaNacimiento = ?,
                    CorreoPersonal = ?, CorreoInstitucional = ?, Telefono = ?, Direccion = ?,
                    PaisOrigen = ?, Nacionalidad = ?, HistorialCiberseguridad = ?,
                    EsExIRSI = ?, FechaIngresoIRSI = ?
                WHERE id = ?
                """,
                becario.nombres, becario.apellidos, Becario._safestr(becario.titulo), Becario._safe_date(becario.fecha_nacimiento),
                Becario._safestr(becario.correo_personal), Becario._safestr(becario.correo_institucional), Becario._safestr(becario.telefono), Becario._safestr(becario.direccion),
                Becario._safestr(becario.pais_origen), Becario._safestr(becario.nacionalidad), Becario._safestr(becario.historial_ciberseguridad),
                bool(becario.es_ex_irsi), Becario._safe_date(becario.fecha_ingreso_irsi), becario.id
            )
            conn.commit()
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al actualizar becario: {sqlstate} - {ex}")
            conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete(becario_id):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Becarios WHERE id = ?", becario_id)
            conn.commit()
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al eliminar becario: {sqlstate} - {ex}")
            conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def find_by_name_and_dob(nombres, apellidos, fecha_nacimiento_str):
        """
        Busca un becario por nombre, apellido y fecha de nacimiento.
        Útil para el mecanismo antifraude.
        """
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            # Asegúrate de que la fecha de nacimiento se formatee correctamente para la DB
            fecha_nacimiento_obj = Becario._safe_date(fecha_nacimiento_str)
            if not fecha_nacimiento_obj:
                return None # No se puede buscar sin una fecha válida

            cursor.execute(
                "SELECT id, Nombres, Apellidos, FechaNacimiento, EsExIRSI FROM Becarios WHERE Nombres = ? AND Apellidos = ? AND FechaNacimiento = ?",
                nombres, apellidos, fecha_nacimiento_obj
            )
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'nombres': row[1],
                    'apellidos': row[2],
                    'fecha_nacimiento': row[3],
                    'es_ex_irsi': bool(row[4])
                }
            return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al buscar becario por nombre y fecha de nacimiento: {sqlstate} - {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Métodos de utilidad para manejar None y fechas
    @staticmethod
    def _safestr(value):
        # Convierte None a cadena vacía para evitar errores de DB en campos NVARCHAR
        return value if value is not None else None # MSSQL maneja NULLs bien, pero a veces es útil convertir a ''

    @staticmethod
    def _safe_date(date_value):
        # Convierte cadenas de fecha a objetos date, maneja None
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, str) and date_value:
            try:
                return date.fromisoformat(date_value) # Espera 'YYYY-MM-DD'
            except ValueError:
                return None
        return None
    
    @staticmethod
    def count_total_becarios():
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Becarios")
            return cursor.fetchone()[0]
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al contar becarios: {sqlstate} - {ex}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def count_ex_irsi_becarios():
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Becarios WHERE es_ex_irsi = 1")
            return cursor.fetchone()[0]
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al contar ex-IRSI: {sqlstate} - {ex}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def count_becarios_by_nationality():
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            # Asumiendo que 'Nacionalidad' es una columna en tu tabla Becarios
            cursor.execute("SELECT Nacionalidad, COUNT(*) FROM Becarios WHERE Nacionalidad IS NOT NULL GROUP BY Nacionalidad ORDER BY COUNT(*) DESC")
            return cursor.fetchall()
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al contar becarios por nacionalidad: {sqlstate} - {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()