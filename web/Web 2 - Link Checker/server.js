const express = require('express');
const axios = require('axios');
const app = express();
const port = 5000;

app.use(express.urlencoded({ extended: true }));

// Ruta restringida a acceso local
app.get('/admin/flag', (req, res) => {
    const remoteIp = req.socket.remoteAddress;
    if (remoteIp === '127.0.0.1' || remoteIp === '::ffff:127.0.0.1' || remoteIp === '::1') {
        res.send('CTFUPB{SSRF_ByP4ss_W1th_D3c1m4l_IP_9921}');
    } else {
        res.status(403).send('Acceso Prohibido: Solo se permite acceso desde localhost');
    }
});

const BLACKLIST = ['localhost', '127.0.0.1', '0.0.0.0', '169.254.169.254', '::1'];

function isBlacklisted(url) {
    try {
        // En un reto de CTF intermedio, a veces el filtro es sobre el string crudo
        // para permitir bypasses mediante representaciones alternativas de la IP.
        // Si usamos 'new URL(url).hostname', Node.js normaliza '127.1' a '127.0.0.1' automáticamente.
        return BLACKLIST.some(item => url.includes(item));
    } catch (e) {
        return true;
    }
}

app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Link Checker</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <style>
                body { background-color: #f0f2f5; padding-top: 50px; }
                .container { max-width: 600px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #004a99; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>UPB Link Checker</h1>
                <p>Verifica si un enlace externo es válido para nuestros boletines.</p>
                <form action="/check" method="POST">
                    <div class="mb-3">
                        <input type="text" name="url" class="form-control" placeholder="http://example.com" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Verificar Enlace</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

app.post('/check', async (req, res) => {
    const targetUrl = req.body.url;

    if (isBlacklisted(targetUrl)) {
        return res.status(403).send('<h1>Acceso Denegado</h1><p>No se permite el acceso a recursos internos o restringidos.</p>');
    }

    try {
        const response = await axios.get(targetUrl, { timeout: 5000 });
        res.send(`<h1>Resultado para: ${targetUrl}</h1><p>Status: ${response.status}</p><pre>${response.data}</pre>`);
    } catch (error) {
        res.status(500).send(`<h1>Error al acceder al enlace</h1><p>${error.message}</p>`);
    }
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Link Checker listening at http://0.0.0.0:${port}`);
});
