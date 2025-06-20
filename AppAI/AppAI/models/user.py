import pyodbc
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def get(user_id):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, role FROM Users WHERE id = ?", int(user_id))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data[0], user_data[1], user_data[2], user_data[3])
            return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al obtener usuario: {sqlstate}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def find_by_username(username):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, role FROM Users WHERE username = ?", username)
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data[0], user_data[1], user_data[2], user_data[3])
            return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al buscar usuario por nombre: {sqlstate}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def create_user(username, password, role):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                           username, hashed_password, role)
            conn.commit()
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al crear usuario: {sqlstate} - {ex}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_users():
        conn = None
        cursor = None
        users = []
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM Users ORDER BY username") # No traer el hash de la contraseña
            for row in cursor.fetchall():
                # No necesitamos el hash para la visualización de la lista
                users.append(User(row[0], row[1], None, row[2]))
            return users
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al obtener todos los usuarios: {sqlstate} - {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    @staticmethod
    def update_user(user_id, username, role, new_password=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            
            if new_password:
                hashed_password = generate_password_hash(new_password)
                cursor.execute(
                    "UPDATE Users SET username = ?, password_hash = ?, role = ? WHERE id = ?",
                    username, hashed_password, role, user_id
                )
            else:
                cursor.execute(
                    "UPDATE Users SET username = ?, role = ? WHERE id = ?",
                    username, role, user_id
                )
            conn.commit()
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al actualizar usuario: {sqlstate} - {ex}")
            conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_user(user_id):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Users WHERE id = ?", user_id)
            conn.commit()
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al eliminar usuario: {sqlstate} - {ex}")
            conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def count_total_users():
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Users")
            return cursor.fetchone()[0]
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al contar usuarios: {sqlstate} - {ex}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def count_users_by_role():
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("SELECT role, COUNT(*) FROM Users GROUP BY role ORDER BY role")
            return cursor.fetchall()
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error al contar usuarios por rol: {sqlstate} - {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()