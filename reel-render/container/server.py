"""Servidor de render dentro del Container de Cloudflare.

POST /render con una receta JSON:
{
  "id": "2026-11-mundial-reel",
  "entradas": {"toma1": "https://.../toma1.mp4", "titulo": "https://.../titulo.png"},
  "pasos": [
    ["ffmpeg", "-i", "{toma1}", "-i", "{titulo}", "-filter_complex", "...", "{salida}"]
  ],
  "salida": "reel.mp4"
}
- Baja cada entrada a una carpeta temporal y reemplaza {nombre} por su ruta.
- {salida} es la ruta del archivo final; {tmp} es la carpeta de trabajo (para intermedios).
- Solo se ejecutan ffmpeg y ffprobe. Devuelve el archivo final.
GET /salud -> ok
"""
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PERMITIDOS = {"ffmpeg", "ffprobe"}
TIPOS = {".mp4": "video/mp4", ".mov": "video/quicktime", ".png": "image/png",
         ".jpg": "image/jpeg", ".webm": "video/webm", ".mp3": "audio/mpeg", ".m4a": "audio/mp4"}


def bajar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": "reel-render"})
    with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f:
        shutil.copyfileobj(r, f)


def renderizar(receta):
    tmp = tempfile.mkdtemp(prefix="render-")
    try:
        rutas = {}
        for nombre, url in (receta.get("entradas") or {}).items():
            ext = os.path.splitext(url.split("?")[0])[1] or ".bin"
            ruta = os.path.join(tmp, f"in_{nombre}{ext}")
            bajar(url, ruta)
            rutas[nombre] = ruta
        salida = os.path.join(tmp, os.path.basename(receta.get("salida") or "salida.mp4"))
        rutas["salida"] = salida
        rutas["tmp"] = tmp
        log = []
        for paso in receta["pasos"]:
            if not paso or paso[0] not in PERMITIDOS:
                raise ValueError(f"comando no permitido: {paso[:1]}")
            args = []
            for a in paso:
                for k, v in rutas.items():
                    a = a.replace("{" + k + "}", v)
                args.append(a)
            if paso[0] == "ffmpeg" and "-y" not in args:
                args.insert(1, "-y")
            p = subprocess.run(args, capture_output=True, text=True, timeout=840)
            log.append((p.stderr or "")[-1500:])
            if p.returncode != 0:
                raise RuntimeError(f"falló {paso[0]} (código {p.returncode}): {p.stderr[-2000:]}")
        with open(salida, "rb") as f:
            datos = f.read()
        return datos, TIPOS.get(os.path.splitext(salida)[1].lower(), "application/octet-stream"), log
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class Manejador(BaseHTTPRequestHandler):
    def _responder(self, codigo, cuerpo, tipo="application/json", extra=None):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        self._responder(200, b'{"ok":true}')

    def do_POST(self):
        if self.path != "/render":
            return self._responder(404, b'{"error":"ruta"}')
        try:
            largo = int(self.headers.get("Content-Length", "0"))
            receta = json.loads(self.rfile.read(largo))
            datos, tipo, _ = renderizar(receta)
            self._responder(200, datos, tipo)
        except Exception as e:  # noqa: BLE001
            self._responder(500, json.dumps({"error": str(e)[-3000:]}).encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    # Como PID 1, Python ignora SIGTERM si no hay handler: sin esto el contenedor
    # nunca se apaga cuando vence sleepAfter y queda facturando 24/7.
    import signal
    import sys
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Manejador).serve_forever()
