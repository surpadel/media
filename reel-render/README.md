# reel-render

Worker + Container (ffmpeg) al lado del media-gateway. Toma recetas de la cola `reel-render`,
baja las entradas por URL, corre los pasos de ffmpeg y deja el resultado en el R2 `media-gateway`
(URL pública `https://media-gateway.nicolas-f-gallo.workers.dev/f/<destino>`).
Estado en el KV del gateway, clave `render:<id>` (`renderizando` → `listo` / `fallido`).

Receta:
```json
{"id": "2026-11-mundial-reel-v1", "destino": "surpadel/reels/2026-11-mundial/reel.mp4",
 "entradas": {"toma1": "https://media-gateway.../f/surpadel/reels/2026-11-mundial/toma1.mp4",
              "titulo": "https://raw.githubusercontent.com/.../titulo.png"},
 "pasos": [["ffmpeg", "-i", "{toma1}", "-i", "{titulo}", "-filter_complex", "...", "{salida}"]],
 "salida": "reel.mp4", "nota": "para qué es"}
```
`{nombre}` = ruta local de cada entrada, `{salida}` = archivo final, `{tmp}` = carpeta para intermedios.
Solo se ejecutan `ffmpeg` y `ffprobe`. Despliegue: workflow "Desplegar reel-render" (necesita los
secretos `CLOUDFLARE_API_TOKEN` y `CLOUDFLARE_ACCOUNT_ID`).
