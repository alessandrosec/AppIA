# Documentación de Prompts del Proyecto IA

Este documento detalla los prompts utilizados en el proyecto, su propósito, los ajustes realizados y los resultados esperados.

## Prompt 1: Generación de Respuesta a Consulta de Usuario

* **Propósito:** Este prompt se utiliza para responder preguntas generales de los usuarios sobre el tema X. Busca proporcionar información concisa y relevante.
* **Prompt Original:** "Por favor, responde a la siguiente pregunta: {pregunta_usuario}"
* **Ajustes Realizados:**
    * **Ajuste 1 (01/06/2025):** Se añadió una instrucción para limitar la respuesta a un máximo de 100 palabras.
        * **Prompt Actual:** "Responde de forma concisa (máximo 100 palabras) a la siguiente pregunta: {pregunta_usuario}"
        * **Razón:** Las respuestas iniciales eran demasiado extensas y a menudo divagaban.
    * **Ajuste 2 (08/06/2025):** Se añadió una directriz para que la respuesta sea en tono formal.
        * **Prompt Actual:** "Responde de forma concisa (máximo 100 palabras) y en un tono formal a la siguiente pregunta: {pregunta_usuario}"
        * **Razón:** El tono informal no era adecuado para el contexto de la aplicación.
* **Resultados Esperados:** Respuestas breves, directas y profesionales, que aborden la consulta del usuario.

## Prompt 2: Resumen de Artículos

* **Propósito:** Generar un resumen de un artículo de noticias dado un texto.
* **Prompt Original:** "Resume el siguiente texto: {texto_articulo}"
* **Ajustes Realizados:**
    * **Ajuste 1 (15/06/2025):** Se especificó que el resumen debe ser en formato de viñetas y no exceder 3 puntos clave.
        * **Prompt Actual:** "Genera un resumen en 3 viñetas con los puntos clave del siguiente texto: {texto_articulo}"
        * **Razón:** Se necesitaba un formato más estructurado y fácil de digerir.
* **Resultados Esperados:** Un resumen de 3 viñetas que capture la esencia del artículo.

---
**Nota:** Es crucial mantener este documento actualizado con cada cambio o adición de prompts.