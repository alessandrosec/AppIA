from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
import pyodbc
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Importa los modelos y rutas de Blueprint
from models.user import User
from routes.auth_routes import auth_bp
from routes.becario_routes import becario_bp
from routes.excel_routes import excel_bp
from routes.admin_routes import admin_bp # Importa el Blueprint de admin

# Inicializa la aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializa Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Registra los Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(becario_bp)
app.register_blueprint(excel_bp)
app.register_blueprint(admin_bp) # Registra el Blueprint de admin

# --- Callbacks de Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# --- Rutas principales ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('dashboard_admin.html')
    elif current_user.role == 'asistente':
        return render_template('dashboard_asistente.html')
    elif current_user.role == 'director':
        return render_template('dashboard_director.html')
    elif current_user.role == 'consulta':
        return render_template('dashboard_consulta.html')
    else:
        flash('Tu rol no tiene un dashboard asignado.', 'danger')
        return redirect(url_for('auth.logout'))

# --- Funcionalidad inicial para crear un usuario admin (solo para desarrollo) ---
# Se mantiene aquí por conveniencia, pero DEBE ser eliminada en producción.
# Es especialmente importante ahora que el admin puede crear otros usuarios.
@app.route('/create_initial_admin')
def create_initial_admin():
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Users WHERE username = ?", 'admin')
        if cursor.fetchone()[0] > 0:
            flash('El usuario admin ya existe.', 'warning')
            return redirect(url_for('auth.login'))

        hashed_password = generate_password_hash('adminpass')
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                       'admin', hashed_password, 'admin')
        conn.commit()
        flash('Usuario admin creado: admin/adminpass. ¡CAMBIAR EN PRODUCCIÓN!', 'success')
        return redirect(url_for('auth.login'))
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        flash(f"Error de base de datos al crear admin: {sqlstate}", 'danger')
        print(f"Error SQL al crear admin: {ex}")
        return "Error al crear admin", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)