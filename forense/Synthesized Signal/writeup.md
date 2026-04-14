# Writeup: Synthesized Signal (Forensics)

## Información del Reto
- **Nombre**: Synthesized Signal
- **Categoría**: Forensics
- **Dificultad**: Media
- **Autor**: __hrcamilo_

## Contexto
Hemos interceptado una transmisión de datos que parece ser una imagen, pero al intentar abrirla, el sistema arroja errores. Los analistas sugieren que las dimensiones de la imagen fueron manipuladas durante la transferencia para ocultar el contenido.

## Objetivo
Reparar el archivo `signal.png` para visualizar la bandera.

---

## Solución Paso a Paso

### 1. Análisis Técnico
Usa `pngcheck` para inspeccionar el archivo:
`pngcheck signal.png`

Verás un error indicando que el CRC del IHDR no coincide con las dimensiones.

### 2. Reparación Binaria
1. Abre `signal.png` con un editor hexadecimal.
2. Ve al bloque IHDR (después de la firma PNG).
3. Cambia los bytes del alto (que estarán en `00 00 00 01`) a un valor más razonable como `00 00 00 64` (100 px).

**Flag**: `CTFUPB{PNG_H3ader_R3p4ir_2024}`
