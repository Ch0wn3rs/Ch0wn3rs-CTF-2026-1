import os
from flask import Flask, request, render_template, jsonify
from lxml import etree

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────────
#  RUTAS DE LA APLICACIÓN
# ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ──────────────────────────────────────────────────────────────────
#  ENDPOINT VULNERABLE  –  POST /api/report
#  Recibe XML crudo (Content-Type: application/xml  o  text/xml)
#  y devuelve los campos extraídos como JSON.
#
#  NOTA: resolve_entities=True + load_dtd=True  →  XXE intencional
# ──────────────────────────────────────────────────────────────────

@app.route('/api/report', methods=['POST'])
def api_report():
    xml_data = request.data

    # También admite el campo "xml_data" de un formulario HTML
    if not xml_data:
        xml_data = (request.form.get('xml_data') or '').encode()

    if not xml_data:
        return jsonify({'error': 'No se proporcionaron datos XML'}), 400

    try:
        # Parser intencionalmente vulnerable para el reto CTF
        parser = etree.XMLParser(
            resolve_entities=True,
            load_dtd=True,
            no_network=False,
        )
        root = etree.fromstring(xml_data, parser)

        result = {'status': 'Reporte procesado exitosamente', 'data': {}}
        for child in root:
            result['data'][child.tag] = child.text or ''

        return jsonify(result)

    except etree.XMLSyntaxError as e:
        return jsonify({'error': f'Error de sintaxis XML: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ──────────────────────────────────────────────────────────────────
#  Endpoint de documentación (pista para el atacante)
# ──────────────────────────────────────────────────────────────────

@app.route('/api/docs')
def api_docs():
    sample = (
        '<?xml version="1.0"?>\n'
        '<pergamino>\n'
        '    <mision>Infiltración en el castillo norte</mision>\n'
        '    <nivel>A</nivel>\n'
        '    <clan>Ch0wn3rs</clan>\n'
        '    <fecha>2024-03-01</fecha>\n'
        '</pergamino>'
    )
    return jsonify({
        'endpoint': '/api/report',
        'method': 'POST',
        'content_type': 'application/xml',
        'sample_body': sample,
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
