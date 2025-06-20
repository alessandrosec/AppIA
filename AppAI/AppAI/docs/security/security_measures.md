# Medidas de Seguridad Implementadas en el Proyecto IA

Este documento describe las prácticas de desarrollo seguro incorporadas en el proyecto, incluyendo la mitigación de vulnerabilidades OWASP y estándares de seguridad.

## 1. Validación y Sanitización de Entrada (Prevención de Inyección de Prompts y SQL)

* **Descripción:** Toda la entrada del usuario es validada y sanitizada antes de ser procesada por la IA o utilizada en consultas SQL.
* **Implementación:**
    * **Python:** Se utilizan funciones `.strip()` para eliminar espacios en blanco y se consideran librerías de validación de esquemas (ej., Pydantic) para asegurar tipos de datos correctos.
    * **SQL (pyodbc):** Se utilizan consultas parametrizadas (`?` en el `db_service.py`) para todas las operaciones de base de datos. Esto previene eficazmente la inyección de SQL al separar los datos de la lógica de la consulta.
    * **IA (OpenAI API):** Aunque OpenAI tiene sus propias defensas, la validación previa en la aplicación añade una capa extra. Se monitorean patrones sospechosos en los prompts de usuario que podrían indicar intentos de "prompt injection".
* **Vulnerabilidades OWASP Cubiertas:**
    * A03:2021-Injection (SQL Injection, Prompt Injection)
    * A01:2021-Broken Access Control (indirectamente, al asegurar que solo datos válidos son procesados)

## 2. Gestión Segura de Credenciales

* **Descripción:** Las claves API y las credenciales de la base de datos se almacenan de forma segura y no se codifican directamente en el código fuente.
* **Implementación:**
    * Se utiliza el archivo `.env` y la librería `python-dotenv` para cargar variables de entorno en tiempo de ejecución.
    * El archivo `.env` está explícitamente incluido en `.gitignore` para evitar que se suba al control de versiones público (ej. GitHub).
* **Estándares Relacionados:** Principio de Mínimo Privilegio.

## 3. Manejo de Errores y Registro (Logging)

* **Descripción:** Se implementa un manejo robusto de errores para evitar la divulgación de información sensible en los mensajes de error. Se registran los errores para auditoría y depuración.
* **Implementación:**
    * Los bloques `try-except` se utilizan extensivamente para capturar excepciones en las interacciones con la base de datos y la API de IA.
    * Los mensajes de error mostrados al usuario son genéricos para evitar revelar detalles internos del sistema.
    * Se utiliza el módulo `logging` de Python para registrar errores y actividades sospechosas en un archivo de log seguro.
* **Vulnerabilidades OWASP Cubiertas:**
    * A09:2021-Security Logging and Monitoring Failures (al implementar logging adecuado).

## 4. Limitación de Recursos y Tasas (Rate Limiting)

* **Descripción:** Para prevenir ataques de denegación de servicio (DoS) y el uso excesivo de recursos de la API, se considera la implementación de límites de tasa.
* **Implementación (Ejemplo - no en el código actual, pero recomendado):**
    * Si se usa Flask, se puede integrar una extensión como `Flask-Limiter` para limitar la cantidad de solicitudes que un usuario puede hacer en un período de tiempo.

---
**Nota:** Este documento se actualizará a medida que se implementen nuevas medidas de seguridad o se identifiquen nuevos riesgos.