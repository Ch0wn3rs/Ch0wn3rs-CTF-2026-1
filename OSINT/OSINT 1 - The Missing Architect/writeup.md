# Writeup: The Geometer's Secret (OSINT)

## Información del Reto
- **Nombre**: The Geometer's Secret
- **Categoría**: OSINT
- **Dificultad**: Facil
- **Autor**: __hrcamilo_

## Contexto
Un antiguo profesor de la UPB dejó un poema cifrado que describe un lugar icónico del campus en Medellín. Se dice que el nombre de la persona que vigila la entrada de este lugar es la clave para acceder a los archivos secretos de la universidad.

## Objetivo
Identificar el lugar descrito en el poema y encontrar el nombre completo del personaje (busto) que se encuentra cerca de la entrada principal del Templo Universitario.

---

## Solución Paso a Paso

Este reto requiere investigación geográfica y el uso de herramientas de visualización de mapas.

### 1. Análisis del Poema
El poema contiene varias pistas clave:
- **"Ciudad de la primavera eterna"**: Medellín, Colombia.
- **"Concha de concreto, blanca y terna"**: Una descripción arquitectónica muy específica que hace referencia al **Templo Universitario Nuestra Señora del Rosario** en el campus de la UPB.
- **"Donde el saber se abraza en un jardín"**: El campus de la UPB Laureles es conocido por ser un ecocampus.

### 2. Localización en Google Maps
Buscamos en Google Maps: `Templo Universitario UPB Medellín`.
- Veremos una estructura blanca circular/parabólica muy distintiva.

### 3. Google Street View
Una vez ubicados en el Templo, bajamos al nivel de la calle (Street View) y exploramos la entrada o los alrededores.
- Cerca de la entrada principal del templo, hay un busto sobre un pedestal de piedra.
- Al acercarnos con Street View, podemos leer la placa de bronce.

### 4. Hallazgo del Personaje
El busto pertenece a: **Félix Henao Botero**.
Él fue el fundador y primer rector de la Universidad Pontificia Bolivariana.

### 5. Formato de la Flag
Siguiendo las instrucciones de "tres palabras" y el formato habitual:
**Flag**: `CTFUPB{Felix_Henao_Botero}`

*(Nota: Los números al final son para mantener la consistencia con otros retos del CTF)*
