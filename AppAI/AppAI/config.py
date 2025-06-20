import os
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()

class Config:
    # Clave secreta para la seguridad de Flask (cambiar en producción)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_cadena_secreta_muy_larga_y_dificil_de_adivinar'

    # Configuración de la base de datos MSSQL
    # Asegúrate de que el driver ODBC esté instalado en el sistema donde se ejecuta la app
    # Para Windows: {ODBC Driver 17 for SQL Server} o {SQL Server}
    # Para Linux (con FreeTDS/unixODBC): {FreeTDS} o el nombre del driver configurado
    # Formato: "DRIVER={Your_ODBC_Driver};SERVER=your_server_ip;DATABASE=your_db_name;UID=your_username;PWD=your_password"
    # Es recomendable usar variables de entorno para las credenciales en producción.
    # Ejemplo con variables de entorno:
    DB_SERVER = os.environ.get('Diego')
    DB_DATABASE = os.environ.get('BecasCiberseguridadDB')
    DB_USERNAME = os.environ.get('DiegoAI')
    DB_PASSWORD = os.environ.get('Muh355718')
    DB_ODBC_DRIVER = os.environ.get('DB_ODBC_DRIVER', '{ODBC Driver 17 for SQL Server}') # Valor por defecto

    # Construye la cadena de conexión
    SQLALCHEMY_DATABASE_URI = (
        f"DRIVER={DB_ODBC_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD}"
    )
    # SQLAlchemy no es estrictamente necesario con pyodbc, pero la variable es común
    # en proyectos Flask con bases de datos. La usaremos para consistencia y futuras expansiones.
    # Para pyodbc directo, solo necesitarías las variables individuales.