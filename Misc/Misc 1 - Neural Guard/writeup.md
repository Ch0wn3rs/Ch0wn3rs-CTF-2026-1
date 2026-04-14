# Writeup: Neural Guard (Misc)

## Información del Reto
- **Nombre**: Neural Guard
- **Categoría**: MISC / PyJail
- **Dificultad**: Media
- **Autor**: __hrcamilo_

## Contexto
Has obtenido acceso a un evaluador de expresiones matemáticas protegido por una "IA de seguridad". Sin embargo, parece que el filtro es puramente sintáctico y bloquea palabras clave específicas. Tu misión es evadir al Guardián Neural y leer el archivo `flag.txt`.

## Objetivo
Leer el archivo `flag.txt` en el servidor remoto.

---

## Solución Paso a Paso

### 1. Análisis del Entorno
Al conectarnos con `nc localhost 1337`, vemos que podemos ejecutar código Python, pero hay una lista negra de palabras prohibidas: `os`, `system`, `flag`, `import`, `eval`, `exec`, `subprocess`, `sh`, `getattr`, `chr`.

### 2. Bypass del Filtro (Concatenación)
Dado que el filtro busca coincidencias exactas de las palabras prohibidas, podemos evadirlo rompiendo las cadenas de texto. El nombre del archivo que queremos leer es `flag.txt`, pero la palabra `flag` está prohibida.

Podemos usar la concatenación de strings de Python:
`'fla' + 'g.txt'`

### 3. Ejecución del Comando
Usamos la función `open()` para leer el archivo. Como `open` no está en la lista negra, podemos usarlo directamente:

**Comando**:
```python
open('fla' + 'g.txt').read()
```

### 4. Resultado
El servidor evaluará la expresión y nos devolverá el contenido del archivo.

**Flag**: `CTFUPB{PyJ41l_3sc4p3_W1th_H3lp_4nd_D1ct_7721}`
