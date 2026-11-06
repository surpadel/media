"""Genera tomas de video e imágenes con la API de APIMart desde GitHub Actions.

Así no se gastan usos del conector de APIMart de Claude: Claude anota el
pedido en apimart/generar.json, hace push, y este script (con el secreto
APIMART_API_KEY del repositorio) pide la toma, espera, la baja al repo y
deja anotados costo y saldo en apimart/registro.json y apimart/saldo.json.

Pedido (cada elemento de apimart/generar.json):
  {
    "id": "2026-11-mundial-toma4",        # único; si ya está en el registro no se repite
    "prompt": "...",
    "modelo": "veo3.1-fast",              # veo3.1-fast | veo3.1-lite | veo3.1-quality
    "resolucion": "1080p",                # 720p | 1080p
    "formato": "9:16",                    # 9:16 | 16:9
    "imagenes": ["https://raw.githubusercontent.com/..."],   # opcional
    "destino": "instagram/2026-11-mundial/reel/toma4.mp4",
    "nota": "para qué es",
    "permitir_caro": false                # obligatorio true para veo3.1-quality
  }

Imágenes (fondos): mismo formato, con un modelo de imagen. Primera opción:
  "modelo": "nano-banana-2"  (= gemini-3.1-flash-image-preview, ~USD 0,02 en 2K)
  "resolucion": "2K"          # 1K | 2K | 4K
  "formato": "9:16"
  "destino": "marca/fondos/fondo-21-algo.png"

Reglas de seguridad:
- Nunca repite un pedido que ya tiene task_id en el registro: si quedó a
  medias, retoma la espera de esa misma tarea (no se cobra dos veces).
- Máximo 2 videos y 10 imágenes nuevos por corrida.
- veo3.1-quality (USD 1 por toma) solo con "permitir_caro": true.
- Destinos solo dentro de las carpetas de APIMART_CARPETAS (por defecto instagram/ y marca/fondos/).
"""
import datetime, json, pathlib, subprocess, sys, time, urllib.error, urllib.request

BASE = "https://api.apimart.ai/v1"
RAIZ = pathlib.Path(__file__).resolve().parent.parent
GEN = RAIZ / "apimart/generar.json"
REG = RAIZ / "apimart/registro.json"
SALDO = RAIZ / "apimart/saldo.json"
MODELOS_BARATOS = {"veo3.1-fast", "veo3.1-lite"}
MODELOS_CAROS = {"veo3.1-quality"}
MAX_NUEVOS = 2          # videos por corrida
MAX_IMAGENES = 10       # imágenes por corrida
# Imágenes: alias amigable -> id de APIMart
MODELOS_IMAGEN = {
    "nano-banana-2": "gemini-3.1-flash-image-preview",
    "gemini-3.1-flash-image-preview": "gemini-3.1-flash-image-preview",
}
# Carpetas donde se puede guardar. Se configuran en el workflow (APIMART_CARPETAS,
# separadas por coma) para que este mismo archivo sirva en cualquier repo.
import os
CARPETAS_OK = tuple(c.strip().strip("/") for c in os.environ.get("APIMART_CARPETAS", "instagram,marca/fondos").split(",") if c.strip())
ESPERA_MAX = 25 * 60  # segundos por tarea
UA = "surpadel-generar/1.0"


def clave():
    import os
    k = os.environ.get("APIMART_API_KEY", "").strip()
    if not k:
        sys.exit("Falta el secreto APIMART_API_KEY en el repositorio.")
    return k


def api(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(BASE + ruta, data=datos, method=metodo, headers={
        "Authorization": f"Bearer {clave()}",
        "Content-Type": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        texto = e.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code} en {ruta}: {texto}") from None


def ahora():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(timespec="seconds")


def leer(p, defecto):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else defecto


def guardar(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def subir(mensaje):
    """Commit + push del registro en el momento (por si el job se corta)."""
    try:
        subprocess.run(["git", "add", "apimart/registro.json", "apimart/saldo.json"], cwd=RAIZ, check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=RAIZ).returncode == 0:
            return
        subprocess.run(["git", "commit", "-m", mensaje + " [skip ci]"], cwd=RAIZ, check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=RAIZ, check=True)
        subprocess.run(["git", "push"], cwd=RAIZ, check=True)
    except Exception as e:
        print("aviso: no pude subir el registro todavía:", e)


def consultar_saldo():
    s = api("GET", "/balance")
    info = {"clave_" + k: s.get(k) for k in ("remain_balance", "used_balance", "unlimited_quota")}
    try:  # saldo de toda la cuenta (la clave puede no tener tope propio)
        c = api("GET", "/user/balance")
        info.update({"cuenta_saldo_usd": c.get("remain_balance"), "cuenta_usado_usd": c.get("used_balance")})
    except Exception as e:
        info["cuenta_error"] = str(e)[:200]
    info["fecha"] = ahora()
    guardar(SALDO, info)
    print("saldo:", info)
    return info


def url_video(tarea):
    res = tarea.get("result") or {}
    for clave_lista in ("videos", "images"):
        for v in res.get(clave_lista) or []:
            if isinstance(v, str):
                return v
            if isinstance(v, dict):
                u = v.get("url")
                if isinstance(u, list):
                    u = u[0] if u else None
                if u:
                    return u
    return None


def es_imagen(p):
    return p.get("modelo") in MODELOS_IMAGEN


def task_id_de(resp):
    d = resp.get("data", resp)
    if isinstance(d, list):
        d = d[0] if d else {}
    tid = d.get("task_id") or d.get("id") if isinstance(d, dict) else None
    if not tid:
        raise RuntimeError("la respuesta no trae task_id: " + json.dumps(resp)[:300])
    return tid


def esperar(task_id, pausa=20):
    inicio = time.time()
    while time.time() - inicio < ESPERA_MAX:
        t = api("GET", f"/tasks/{task_id}?language=es")
        t = t.get("data", t) if isinstance(t.get("data"), dict) else t
        estado = t.get("status")
        print(f"  {task_id}: {estado} {t.get('progress', '')}%")
        if estado in ("completed", "failed", "cancelled"):
            return t
        time.sleep(pausa)
    return {"status": "esperando", "id": task_id}


def bajar(url, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        datos = r.read()
    if len(datos) < 10_000:
        raise ValueError(f"archivo muy chico ({len(datos)} bytes)")
    destino.write_bytes(datos)
    return len(datos)


def validar(p):
    for campo in ("id", "prompt", "modelo", "destino"):
        if not p.get(campo):
            return f"falta '{campo}'"
    if p["modelo"] in MODELOS_CAROS and not p.get("permitir_caro"):
        return f"{p['modelo']} es caro: requiere \"permitir_caro\": true"
    if p["modelo"] not in MODELOS_BARATOS | MODELOS_CAROS | set(MODELOS_IMAGEN):
        return f"modelo no habilitado: {p['modelo']}"
    destino = str((RAIZ / p["destino"]).resolve())
    if not any(destino.startswith(str(RAIZ / c) + "/") for c in CARPETAS_OK):
        return "destino fuera de " + " o ".join(c + "/" for c in CARPETAS_OK)
    return None


def main():
    pedidos = leer(GEN, [])
    registro = leer(REG, {})
    saldo_inicial = consultar_saldo()
    nuevos = 0
    nuevas_img = 0
    errores = 0

    for p in pedidos:
        pid = p.get("id", "?")
        r = registro.get(pid, {})
        if r.get("estado") in ("listo", "rechazado", "fallido"):
            continue
        problema = validar(p)
        if problema:
            print(f"{pid}: rechazado ({problema})")
            registro[pid] = {"estado": "rechazado", "motivo": problema, "fecha": ahora()}
            errores += 1
            continue

        if not r.get("task_id"):
            imagen = es_imagen(p)
            if imagen and nuevas_img >= MAX_IMAGENES or not imagen and nuevos >= MAX_NUEVOS:
                print(f"{pid}: queda para la próxima corrida (tope por corrida)")
                continue
            if imagen:
                cuerpo = {
                    "model": MODELOS_IMAGEN[p["modelo"]],
                    "prompt": p["prompt"],
                    "size": p.get("formato", "9:16"),
                    "resolution": p.get("resolucion", "2K"),
                    "n": 1,
                }
                ruta = "/images/generations"
            else:
                cuerpo = {
                    "model": p["modelo"],
                    "prompt": p["prompt"],
                    "duration": 8,
                    "aspect_ratio": p.get("formato", "9:16"),
                    "resolution": p.get("resolucion", "1080p"),
                }
                ruta = "/videos/generations"
            if p.get("imagenes"):
                cuerpo["image_urls"] = p["imagenes"]
            print(f"{pid}: pidiendo {cuerpo['model']} {cuerpo['resolution']}")
            try:
                resp = api("POST", ruta, cuerpo)
                task_id = task_id_de(resp)
            except Exception as e:
                print(f"{pid}: error al pedir -> {e}")
                registro[pid] = {"estado": "fallido", "motivo": str(e)[:300], "fecha": ahora()}
                errores += 1
                continue
            if imagen:
                nuevas_img += 1
            else:
                nuevos += 1
            r = {"estado": "pedido", "task_id": task_id, "modelo": p["modelo"],
                 "destino": p["destino"], "nota": p.get("nota", ""), "pedido": ahora()}
            registro[pid] = r
            guardar(REG, registro)
            subir(f"APIMart: pedido {pid}")

        t = esperar(r["task_id"], pausa=8 if es_imagen(p) else 20)
        estado = t.get("status")
        if estado == "completed":
            url = url_video(t)
            r.update({"costo_usd": t.get("cost"), "creditos": t.get("credits_cost"),
                      "segundos": t.get("actual_time"), "url": url})
            try:
                if not url:
                    raise ValueError("la tarea terminó sin URL: " + json.dumps(t.get("result"))[:300])
                tam = bajar(url, RAIZ / p["destino"])
                r.update({"estado": "listo", "kb": tam // 1024, "terminado": ahora()})
                print(f"{pid}: listo -> {p['destino']} ({tam // 1024} KB, USD {t.get('cost')})")
            except Exception as e:
                r.update({"estado": "sin_bajar", "motivo": str(e)[:300]})
                print(f"{pid}: terminó pero no se pudo bajar -> {e}")
                errores += 1
        elif estado in ("failed", "cancelled"):
            r.update({"estado": "fallido", "motivo": json.dumps(t.get("error"), ensure_ascii=False)[:300],
                      "terminado": ahora()})
            print(f"{pid}: {estado} -> {r['motivo']}")
            errores += 1
        else:
            r["estado"] = "esperando"
            print(f"{pid}: sigue en proceso; la próxima corrida retoma la misma tarea")
        registro[pid] = r
        guardar(REG, registro)

    if nuevos or nuevas_img or any(v.get("estado") == "listo" for v in registro.values()):
        try:
            consultar_saldo()
        except Exception as e:
            print("no pude releer el saldo:", e)
    guardar(REG, registro)
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
