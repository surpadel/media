import { Container, getContainer } from "@cloudflare/containers";

interface Env {
  RENDER: DurableObjectNamespace<Render>;
  ESTADO: KVNamespace; // mismo KV del media-gateway
  MEDIA: R2Bucket; // mismo R2 del media-gateway
  BASE_PUBLICA: string; // https://media-gateway.nicolas-f-gallo.workers.dev/f/
}

interface Receta {
  id: string;
  destino: string; // ruta en R2, ej. surpadel/reels/2026-11-mundial/reel.mp4
  entradas?: Record<string, string>;
  pasos: string[][];
  salida?: string;
  nota?: string;
}

export class Render extends Container {
  defaultPort = 8080;
  sleepAfter = "3m";
}

const clave = (id: string) => `render:${id}`;

async function guardar(env: Env, id: string, datos: Record<string, unknown>) {
  await env.ESTADO.put(clave(id), JSON.stringify({ ...datos, actualizado: new Date().toISOString() }));
}

async function procesar(r: Receta, env: Env) {
  if (!r.id || !r.destino || !Array.isArray(r.pasos) || !r.pasos.length) {
    await guardar(env, r.id || "sin-id", { estado: "rechazado", motivo: "faltan id, destino o pasos" });
    return;
  }
  const previo = await env.ESTADO.get(clave(r.id), "json") as { estado?: string } | null;
  if (previo?.estado === "listo") return; // mismo id no se vuelve a renderizar
  const inicio = Date.now();
  await guardar(env, r.id, { estado: "renderizando", destino: r.destino, nota: r.nota });
  try {
    const c = getContainer(env.RENDER, r.id);
    const resp = await c.fetch(new Request("http://render/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(r),
    }));
    if (!resp.ok) {
      const txt = await resp.text();
      await guardar(env, r.id, { estado: "fallido", motivo: txt.slice(-3000), destino: r.destino });
      return;
    }
    const datos = await resp.arrayBuffer();
    await env.MEDIA.put(r.destino, datos, {
      httpMetadata: { contentType: resp.headers.get("Content-Type") || "video/mp4" },
    });
    await guardar(env, r.id, {
      estado: "listo",
      destino: r.destino,
      url_publica: env.BASE_PUBLICA + r.destino,
      kb: Math.round(datos.byteLength / 1024),
      segundos: Math.round((Date.now() - inicio) / 1000),
      nota: r.nota,
    });
  } catch (e) {
    await guardar(env, r.id, { estado: "fallido", motivo: String(e).slice(-3000), destino: r.destino });
  }
}

export default {
  async queue(batch: MessageBatch<Receta>, env: Env) {
    for (const m of batch.messages) {
      await procesar(m.body, env);
      m.ack();
    }
  },
  async fetch(req: Request, env: Env) {
    const url = new URL(req.url);
    const m = url.pathname.match(/^\/estado\/(.+)$/);
    if (m) {
      const v = await env.ESTADO.get(clave(decodeURIComponent(m[1])));
      return new Response(v || '{"estado":"desconocido"}', { headers: { "Content-Type": "application/json" } });
    }
    return new Response("reel-render: mandá recetas a la cola reel-render", { status: 200 });
  },
} satisfies ExportedHandler<Env, Receta>;
