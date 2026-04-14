# Writeup – Territorio Chown3rs

**Flag real:** `ctfupb{t3rr1t0r10_ch0wn3rs}`

---

## Paso 1 – Revisar metadatos

```bash
strings territorio.png | grep -i "ctfupb\|comment\|author"
```

Salida:
```
Territorio Chown3rs - ctfupb{h4ck34m3_s1_pu3d35}
```

La flag en los metadatos es **falsa**. Hay que mirar más profundo.

También se puede usar `exiftool` si está disponible:

```bash
exiftool territorio.png
```

---

## Paso 2 – Identificar esteganografía LSB

La pista del reto menciona el **bit menos significativo (LSB)** y el **canal rojo**.

La técnica LSB (Least Significant Bit) consiste en almacenar cada bit del mensaje
en el bit de menor peso de cada píxel, de modo que el cambio en el color es
imperceptible al ojo humano.

---

## Paso 3 – Extraer la flag oculta

```python
from PIL import Image

img = Image.open("territorio.png")
pixels = list(img.getdata())

# Extraer LSB del canal rojo
bits = [r & 1 for r, g, b in pixels]

# Reconstruir bytes de 8 bits
flag_bytes = []
for i in range(0, len(bits) - 7, 8):
    byte = 0
    for j in range(8):
        byte = (byte << 1) | bits[i + j]
    if byte == 0:      # terminador nulo
        break
    flag_bytes.append(byte)

print(bytes(flag_bytes).decode())
```

Resultado:
```
ctfupb{t3rr1t0r10_ch0wn3rs}
```

---

## Resumen de herramientas

| Herramienta | Uso |
|-------------|-----|
| `strings` / `exiftool` | Revelar metadatos y flag falsa |
| Python + Pillow | Extraer bits LSB del canal rojo |

---

## Concepto clave: LSB Steganography

Cada píxel RGB tiene 3 valores de 8 bits (0-255). El LSB de cada componente
solo afecta el color en 1/255 ≈ 0.4%, completamente invisible.
Usando el LSB del canal rojo se pueden almacenar 1 bit por píxel,
lo que equivale a 1 byte cada 8 píxeles. Una imagen de 64×64 = 4096 píxeles
puede ocultar hasta 512 bytes de datos.
