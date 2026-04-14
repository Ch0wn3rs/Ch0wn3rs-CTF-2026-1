# Writeup: The Eye of the Ancestor (OSINT)

## Información del Reto
- **Nombre**: The Eye of the Ancestor
- **Categoría**: OSINT
- **Dificultad**: Avanzada
- **Autor**: __hrcamilo_

## Contexto
Se ha encontrado un manuscrito antiguo que habla del "Ombligo del Mundo". En él, se describe a un guardián solitario que es el único capaz de ver el regreso de los navegantes. Quien encuentre su nombre, encontrará la paz.

## Objetivo
Identificar el nombre específico de la plataforma o del Moai descrito en el poema.

---

## Solución Paso a Paso

Este reto requiere una investigación global y el uso de técnicas de búsqueda inversa y descriptiva.

### 1. El Ombligo del Mundo
La frase **"En el ombligo del mundo"** es una traducción directa de **"Te Pito o te Henua"**, que es uno de los nombres tradicionales de la **Isla de Pascua (Easter Island / Rapa Nui)** en Chile.

### 2. Los Gigantes de Piedra
Se refiere claramente a los **Moai**. La pista clave es: **"Solo uno de ellos recuperó la mirada"**.
- La gran mayoría de los Moai en la isla no tienen ojos (las cuencas están vacías).
- Históricamente, se cree que los Moai tenían "ojos de coral" que se insertaban al finalizar la estatua. Solo uno fue restaurado con sus ojos de coral y obsidiana.

### 3. El Solitario con Sombrero
Investigando moais con ojos y sombrero (Pukao):
- Buscamos en Google: `Moai with eyes restored` o `Only moai with eyes Easter Island`.
- Los resultados apuntan a la zona de **Tahai**.
- En el complejo de Tahai, hay tres plataformas (Ahus). El Moai solitario que tiene ojos y lleva un Pukao (sombrero de piedra roja) se encuentra en el **Ahu Ko Te Riku**.

### 4. Verificación en Google Maps
Buscamos en Google Maps: `Ahu Ko Te Riku`.
- Podemos ver en las fotos y en Street View al Moai solitario con sus ojos blancos y su sombrero rojo mirando hacia el interior de la isla.

### 5. Flag
El nombre de la plataforma es la clave.
**Flag**: `CTFUPB{Ahu_Ko_Te_Riku}`
