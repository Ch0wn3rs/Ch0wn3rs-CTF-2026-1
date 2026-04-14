# Writeup: Link Checker

## Información del Reto
- **Nombre**: Link Checker
- **Categoría**: Web
- **Dificultad**: Intermedia
- **Autor**: __hrcamilo_

## Contexto
El departamento de comunicaciones utiliza una herramienta interna para verificar que los enlaces externos en sus boletines no estén rotos. Sin embargo, un investigador de seguridad notó que la herramienta no valida correctamente las peticiones. ¿Podrás acceder al servicio secreto interno?

## Objetivo
Acceder a `http://127.0.0.1:5000/admin/flag` desde el propio servidor.

---

## Solución

### 1. Análisis Inicial
La aplicación recibe una URL y realiza una petición GET hacia ella, mostrando el código de estado y el contenido. Esto es un escenario clásico de **SSRF (Server-Side Request Forgery)**.

El objetivo es tratar de que el servidor haga una petición a su propia interfaz de loopback (`127.0.0.1`) en el puerto `5000` (el mismo donde está el reto), donde corre el endpoint restringido de la bandera.

### 2. Prueba de SSRF Básico
Si intentamos acceder directamente a `http://127.0.0.1:5000/admin/flag` o `http://localhost:5000/admin/flag`, el servidor responde con:
`<h1>Acceso Denegado</h1><p>No se permite el acceso a recursos internos o restringidos.</p>`

Esto confirma que existe una **lista negra (blacklist)** que bloquea explícitamente estas direcciones antes de realizar la petición.

### 3. Evadiendo el Filtro
Dado que el filtro solo bloquea cadenas exactas como `127.0.0.1` o `localhost`, podemos usar representaciones alternativas de la IP de loopback que el sistema operativo y las librerías de red (como `axios`) resolverán correctamente a `127.0.0.1`.

#### Opción A: IP Decimal
La dirección `127.0.0.1` se puede convertir a un único número entero (decimal):
`2130706433`
Payload: `http://2130706433:5000/admin/flag`

#### Opción B: Punto Abreviado
Muchos sistemas permiten omitir los ceros intermedios:
Payload: `http://127.1:5000/admin/flag`

#### Opción C: Notación Octal
También podemos representar cada octeto en octal (anteponiendo un 0):
Payload: `http://0177.0.0.1:5000/admin/flag`

### 4. Ejecución y Flag
Al ingresar cualquiera de estos payloads (por ejemplo, `http://127.1:5000/admin/flag`) en el formulario del portal (en `http://localhost:5000`), el filtro no detectará la cadena prohibida, pero la petición llegará al servicio interno.

Al llegar la petición desde `127.0.0.1`, el endpoint `/admin/flag` nos entregará el secreto.

**Flag**: `CTFUPB{SSRF_ByP4ss_W1th_D3c1m4l_IP_9921}`
