# Casos de Prueba Funcionales del Proyecto IA

Este documento detalla los casos de prueba para verificar la funcionalidad del sistema, incluyendo los pasos, datos de entrada esperados y resultados esperados.

## 1. Generación de Texto de IA

* **ID del Caso de Prueba:** TC-AI-001
* **Objetivo:** Verificar que la IA genera una respuesta coherente a un prompt válido.
* **Precondiciones:** El servicio de IA está configurado y accesible.
* **Pasos:**
    1.  Enviar una solicitud POST a `/generate` con el JSON: `{"prompt": "¿Cuál es la capital de Francia?"}`
* **Datos de Entrada:** `{"prompt": "¿Cuál es la capital de Francia?"}`
* **Resultado Esperado:**
    * Código de estado HTTP: 200 OK
    * JSON de respuesta: `{"response": "La capital de Francia es París."}` (o una respuesta similar y correcta).
    * El prompt y la respuesta se registran en la base de datos.
* **Estado:** Pendiente/En Curso/Aprobado

* **ID del Caso de Prueba:** TC-AI-002
* **Objetivo:** Verificar que la IA maneja prompts vacíos.
* **Precondiciones:** El servicio de IA está configurado y accesible.
* **Pasos:**
    1.  Enviar una solicitud POST a `/generate` con el JSON: `{"prompt": ""}`
* **Datos de Entrada:** `{"prompt": ""}`
* **Resultado Esperado:**
    * Código de estado HTTP: 400 Bad Request
    * JSON de respuesta: `{"error": "No se proporcionó un prompt"}`
* **Estado:** Pendiente/En Curso/Aprobado

## 2. Interacción con la Base de Datos

* **ID del Caso de Prueba:** TC-DB-001
* **Objetivo:** Verificar la inserción de datos en la tabla `AiInteractions`.
* **Precondiciones:** La base de datos está conectada y la tabla `AiInteractions` existe.
* **Pasos:**
    1.  Disparar una llamada a `/generate` con un prompt válido.
    2.  Conectarse directamente a la base de datos y ejecutar `SELECT * FROM AiInteractions ORDER BY timestamp DESC`.
* **Datos de Entrada:** (Implícito desde TC-AI-001)
* **Resultado Esperado:**
    * Una nueva fila existe en `AiInteractions` con el `prompt` y la `response` correctos.
* **Estado:** Pendiente/En Curso/Aprobado

## 3. Acceso a Datos de la Base de Datos (Ruta `/data`)

* **ID del Caso de Prueba:** TC-DB-002
* **Objetivo:** Verificar que la ruta `/data` devuelve datos de la base de datos.
* **Precondiciones:** La base de datos está conectada y la tabla `YourTable` tiene datos.
* **Pasos:**
    1.  Enviar una solicitud GET a `/data`.
* **Datos de Entrada:** N/A
* **Resultado Esperado:**
    * Código de estado HTTP: 200 OK
    * JSON de respuesta que contiene una lista de objetos de datos de `YourTable`.
* **Estado:** Pendiente/En Curso/Aprobado

---
**Nota:** Mantener este documento actualizado y registrar los resultados de cada prueba.