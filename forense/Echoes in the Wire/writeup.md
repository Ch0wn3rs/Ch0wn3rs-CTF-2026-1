# Writeup: Echoes in the Wire (Forensics)

## Información del Reto
- **Nombre**: Echoes in the Wire
- **Categoría**: Forensics / Network
- **Dificultad**: Media
- **Autor**: __hrcamilo_

## Contexto
Se ha detectado tráfico extraño saliendo de la red de Nexus-Tech. Los analistas creen que un ex-empleado está utilizando protocolos básicos para evadir la detección y extraer información sensible poco a poco. Hemos capturado una muestra de este tráfico en un archivo `.pcap`.

## Objetivo
Analizar la captura de red `capture.pcap` y extraer la bandera oculta en los paquetes.

---

## Solución Paso a Paso

Este reto se enfoca en el análisis de tráfico de red y la extracción de payloads.

### 1. Inspección Inicial (Wireshark)
Al abrir `capture.pcap` con Wireshark, verás una gran cantidad de tráfico **HTTP, DNS y TCP** que actúa como ruido para ocultar la actividad real. 
- Hay cientos de paquetes que no parecen tener un propósito claro.
- **Estrategia**: Debes aplicar un filtro para buscar protocolos inusuales o patrones de exfiltración.

### 2. Filtrado de Ruido
Dado que sospechamos de protocolos básicos, filtramos por **ICMP**.
- **Filtro en Wireshark**: `icmp`
- Ahora verás una secuencia de paquetes **ICMP Echo (ping) Requests** intercalados con pings falsos (junk data).

### 3. Identificación del Canal de Datos
Al examinar los paquetes ICMP filtrados, notarás que algunos contienen caracteres legibles al inicio de su sección "Data".
- El primer paquete relevante tiene `U`.
- El siguiente tiene `P`.
- **Dificultad**: Deberás ignorar los pings que contienen datos aleatorios (basura) y centrarte en los que siguen el patrón de la bandera.

### 4. Automatización de la Extracción
Extraer los caracteres manualmente en medio de tanto ruido es tedioso. Usar `tshark` es la mejor opción.

**Comando**:
```bash
tshark -r capture.pcap -Y "icmp.type==8" -T fields -e data | xxd -r -p
```
*Explicación*:
- `-r`: Lee el archivo.
- `-Y "icmp.type==8"`: Filtra solo los Echo Requests.
- `-T fields -e data`: Extrae solo el campo hexadecimal de los datos.
- `xxd -r -p`: Convierte el hexadecimal de vuelta a texto ASCII.

### 4. Resultado Final
Al ejecutar el comando, se reconstruirá la cadena completa:
`CTFUPB{ICMP_Tunn3l1ng_F0und_4421}\x00\x00...`

**Flag**: `CTFUPB{ICMP_Tunn3l1ng_F0und_4421}`
