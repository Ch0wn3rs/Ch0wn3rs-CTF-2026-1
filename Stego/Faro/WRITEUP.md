## Writeup — WhatIsThis

### Solución
Luego de descargar el archivo WAV y abrirlo, se puede escuchar un mensaje en código morse, que al decodificarse muestra la siguiente cadena: `NB2HI4DTHIXS6ZDSNF3GKLTHN5XWO3DFFZRW63JPOVRT6ZLYOBXXE5B5MRXXO3TMN5QWIJTJMQ6TC5CBJFEEOUCJGNMEQYRSIVVFCMKJNFVHG4DZNRUEU3TSJ42FQVDU` <br>

Esta cadena está en base32 como se puede ver en el comentario de los metadatos del archivo "signal.wav", por lo que se decodifica y se obtiene un [enlace a Drive](https://drive.google.com/uc?export=download&id=1tAIHGPI3XHb2EjQ1IijspylhJnrO4XTt) <br>

Siguiendo este enlace, se descarga una imagen llamada "Faro.jpg", en la cual, al mirar sus metadatos con `exiftool`, se puede ver algo que parece una flag `PGSHCO{f13zcer_f3_e3i1f4a_y0f_z3g4q4g0f}` <br>

Finalmente se decodifica la flag, al cual estaba codificada en rot13 y se obtiene la real: `CTFUPB{s13mpre_s3_r3v1s4n_l0s_m3t4d4t0s}` <br>
