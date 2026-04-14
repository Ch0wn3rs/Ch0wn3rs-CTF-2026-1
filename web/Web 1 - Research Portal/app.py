from flask import Flask, request, render_template_string, render_template
import os

app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = 'upb_internal_secret_key_2026'

# Filtro simple para dificultad intermedia
BLACKLIST = ['class', 'mro', 'subclasses', 'config', 'self', 'request', 'import', 'builtins', 'eval']

def is_valid(payload):
    for word in BLACKLIST:
        if word in payload.lower():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    name = request.args.get('name', 'Investigador')
    
    # Vulnerabilidad: SSTI
    # Se renderiza el nombre directamente en el string del template
    template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard - Research Portal</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body {{ background-color: #f8f9fa; }}
            .hero {{ background: linear-gradient(135deg, #0d6efd, #0dcaf0); color: white; padding: 60px 0; }}
        </style>
    </head>
    <body>
        <div class="hero text-center">
            <h1>Bienvenido al Portal de Investigación, {name}!</h1>
            <p>Tu sesión está activa.</p>
        </div>
        <div class="container mt-5">
            <h3>Notificaciones Recientes</h3>
            <ul class="list-group">
                <li class="list-group-item">Nuevo paper publicado sobre IA generativa.</li>
                <li class="list-group-item">Mantenimiento de servidores programado para el domingo.</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    if not is_valid(name):
        return "<h1>Error: Intento de intrusión detectado.</h1><p>El uso de palabras clave reservadas está prohibido.</p>", 403

    return render_template_string(template)

if __name__ == '__main__':
    # El archivo flag.txt debe estar en el mismo directorio o raíz
    # Se puede configurar como variable de entorno también
    app.run(host='0.0.0.0', port=5000)
