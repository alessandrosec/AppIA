import pyodbc
from config import Config
from datetime import datetime

class AuditLog:
    def __init__(self, id, timestamp, user_id, username, action_type, description, ip_address):
        self.id = id
        self.timestamp = timestamp
        self.user_id = user_id
        self.username = username
        self.action_type = action_type
        self.description = description
        self.ip_address = ip_address

    @staticmethod
    def log_action(user_id, username, action_type, description, ip_address):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO AuditLogs (user_id, username, action_type, description, ip_address)
                VALUES (?, ?, ?, ?, ?)
                """,
                user_id, username, action_type, description, ip_address
            )
            conn.commit()
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al registrar auditoría: {sqlstate} - {ex}")
            conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_logs():
        conn = None
        cursor = None
        logs = []
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, user_id, username, action_type, description, ip_address FROM AuditLogs ORDER BY timestamp DESC")
            for row in cursor.fetchall():
                logs.append(AuditLog(*row))
            return logs
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al obtener logs de auditoría: {sqlstate} - {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()