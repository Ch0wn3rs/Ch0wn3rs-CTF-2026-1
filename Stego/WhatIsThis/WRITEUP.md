## Writeup — WhatIsThis

### Solución
Luego de descargar el archivo, se puede ver que no se puede descomprimir el archivo zip, esto hace pensar que realmente no es ese tipo de archivo por lo que utiliza `file` para identificarlo. <br>

Luego de saber que es un archivo WAV, el siguiente paso es escucharlo y en este caso no hay nada relevante en el sonido, por lo que, al ser un reto de esteganografía, se intenta extraer algún archivo embebido con `steghide extract -sf WhatIsThis.zip` sin proporcionar contraseña. <br>

Se extrae un archivo zip, que tiene unas imagenes al interior, por lo que se revisan y se puede identificar que todas las imágenes son de Resident Evil Village. <br>

Al ver los pesos de las imagenes, hay dos que superan por mucho las otras, por lo que se intenta usar `steghide extract -sf` con dichas imagenes proporcionando como contraseña "village" y en la cuarta imagen se extrae correctamente la flag `CTFUPB{why_u_l00k1ng_4t_d1m1tr3scu?}`
