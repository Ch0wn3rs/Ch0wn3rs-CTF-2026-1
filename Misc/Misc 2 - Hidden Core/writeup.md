# Writeup: Hidden Core (Misc)

## Información del Reto
- **Nombre**: Hidden Core
- **Categoría**: MISC / Forensics / Stegano
- **Dificultad**: Media
- **Autor**: __hrcamilo_

## Contexto
Has obtenido una imagen del núcleo de un sistema cuántico. Los analistas creen que hay información sensible oculta en esta imagen, protegida por una clave que solo el sistema conoce. ¿Podrás extraer el secreto?

## Objetivo
Encontrar la bandera oculta dentro del archivo `core.jpg`.

---

## Solución Paso a Paso

### 1. Análisis de Metadatos
Usa `exiftool` para revisar la imagen:
`exiftool core.jpg`

Encontrarás un campo de comentario:
`System Password: C0r3_Fr4mew0rk_2024`

### 2. Extracción de Archivo
La imagen tiene un archivo ZIP concatenado. Usa `binwalk` para extraerlo:
`binwalk -e core.jpg`

### 3. Desbloqueo
Entra en la carpeta extraída y abre el archivo ZIP usando la contraseña:
`C0r3_Fr4mew0rk_2024`

**Flag**: `CTFUPB{H1dd3n_1n_Pl41n_S1ght_4482}`
