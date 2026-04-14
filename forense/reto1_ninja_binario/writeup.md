# Writeup – Ninja en las Sombras

**Flag real:** `ctfupb{n1nj4_d3_n0ch3}`

---

## Paso 1 – Ejecutar el binario

```bash
chmod +x ninja_sombras
./ninja_sombras
```

Salida:
```
== Ninja en las Sombras ==
El ninja siempre deja una pista falsa:
FLAG: ctfupb{h4ck34m3_s1_pu3d35}
Pero las sombras ocultan más de lo que ves...
```

La flag impresa es **falsa**. El mensaje al final es una pista de que hay más oculto.

---

## Paso 2 – Analizar con `strings`

```bash
strings ninja_sombras
```

Entre la salida aparecen dos cadenas importantes:

```
XOR42
FLAG: ctfupb{h4ck34m3_s1_pu3d35}
```

La cadena `XOR42` indica que algo está codificado con XOR usando la clave `0x42`.

---

## Paso 3 – Inspeccionar con `xxd`

```bash
xxd ninja_sombras | grep -B1 "XOR42"
```

Se pueden ver bytes antes de la cadena `XOR42`:

```
00002010: 2136 2437 3220 392c 732c 2876 1d26 711d  !6$72 9,s,(v.&q.
00002020: 2c72 212a 713f 0058 4f52 3432 00         ,r!*q?.XOR42.
```

Los bytes `21 36 24 37 32 20 39 2c 73 2c 28 76 1d 26 71 1d 2c 72 21 2a 71 3f`
terminados en `00` son la flag cifrada. El nulo `00` indica el final de la cadena.

---

## Paso 4 – Decodificar con XOR

```python
encoded = [
    0x21, 0x36, 0x24, 0x37, 0x32, 0x20, 0x39,
    0x2c, 0x73, 0x2c, 0x28, 0x76, 0x1d, 0x26,
    0x71, 0x1d, 0x2c, 0x72, 0x21, 0x2a, 0x71, 0x3f
]
key = 0x42
flag = ''.join(chr(b ^ key) for b in encoded)
print(flag)
```

Resultado:
```
ctfupb{n1nj4_d3_n0ch3}
```

---

## Resumen de herramientas

| Herramienta | Uso |
|-------------|-----|
| `strings` | Encontrar cadenas legibles + hint `XOR42` |
| `xxd` | Ver bytes crudos del binario |
| Python | Decodificar XOR con clave 0x42 |
