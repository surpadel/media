"""Estilo 'transmisión de circuito pro': marcadores tipo TV, títulos metalizados, franjas de luz."""
import sys, json, pathlib
import gen
from playwright.sync_api import sync_playwright

T = gen.THEMES

def base_css(t, W, H, fondo):
    bg = gen.b64(gen.D / fondo)
    pos = gen.POS.get(fondo, "center")
    return gen.FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:B;color:#fff;position:relative;
 background:#050b16 url(data:image/{"jpeg" if fondo.endswith(".jpg") else "webp"};base64,{bg}) {pos}/cover}}
.shade{{position:absolute;inset:0;background:
 radial-gradient(ellipse 120% 70% at 50% 45%,rgba(5,11,22,0),rgba(5,11,22,.75) 85%),
 linear-gradient(180deg,rgba(5,11,22,.8) 0%,rgba(5,11,22,.2) 30%,rgba(5,11,22,.3) 60%,rgba(5,11,22,.92) 100%)}}
.streak{{position:absolute;left:-30%;width:160%;height:3px;background:linear-gradient(90deg,transparent,{t['acc']}cc,#fff,{t['acc']}cc,transparent);transform:rotate(-12deg);opacity:.55;filter:blur(.5px)}}
.flare{{position:absolute;width:520px;height:520px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.35),rgba(255,255,255,0) 60%);mix-blend-mode:screen}}
.grain{{position:absolute;inset:0;opacity:.07;background-image:repeating-radial-gradient(circle at 17% 32%,#fff 0 1px,transparent 1px 3px)}}
.wrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center}}
.strip{{display:flex;align-items:stretch;height:64px;font-weight:700;letter-spacing:3px;text-transform:uppercase;font-size:24px;box-shadow:0 8px 30px rgba(0,0,0,.5)}}
.strip .a{{background:{t['hot']};color:#071528;display:flex;align-items:center;padding:0 22px;font-family:BC;font-style:italic;font-weight:800;font-size:34px;letter-spacing:1px;clip-path:polygon(0 0,100% 0,92% 100%,0 100%);padding-right:40px}}
.strip .b{{background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;padding:0 26px 0 30px;margin-left:-14px;clip-path:polygon(4% 0,100% 0,100% 100%,0 100%)}}
.logo{{width:120px;height:120px;filter:drop-shadow(0 6px 24px rgba(0,0,0,.6))}}
.kick{{font-weight:700;letter-spacing:8px;font-size:26px;color:{t['acc']};text-transform:uppercase}}
.metal{{font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.88;text-align:center;
 background:linear-gradient(180deg,#fff 0%,#fff 45%,#c9d6e6 55%,#fff 100%);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 6px 20px rgba(0,0,0,.7))}}
.gold{{background:linear-gradient(180deg,#ffe9a8 0%,{t['hot']} 45%,#b77a00 58%,{t['hot']} 100%);-webkit-background-clip:text;color:transparent}}
.sb{{width:100%;background:linear-gradient(180deg,rgba(10,22,42,.94),rgba(5,12,24,.94));border:1px solid rgba(255,255,255,.16);border-radius:6px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.45)}}
.sb .hd{{display:flex;justify-content:space-between;align-items:center;background:linear-gradient(90deg,{t['court2']},{t['court']});padding:6px 18px;font-weight:700;font-size:20px;letter-spacing:3px;text-transform:uppercase}}
.row{{display:flex;align-items:center;height:62px;border-top:1px solid rgba(255,255,255,.08)}}
.row .nm{{flex:1;padding:0 18px;font-size:31px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:rgba(255,255,255,.62)}}
.row.w .nm{{color:#fff;font-weight:700}}
.row .tri{{width:0;height:0;border-left:14px solid {t['hot']};border-top:10px solid transparent;border-bottom:10px solid transparent;margin-left:16px;visibility:hidden}}
.row.w .tri{{visibility:visible}}
.set{{width:62px;height:100%;display:flex;align-items:center;justify-content:center;font-family:BC;font-weight:800;font-style:italic;font-size:40px;color:rgba(255,255,255,.55);border-left:1px solid rgba(255,255,255,.08)}}
.set.won{{background:{t['hot']};color:#071528}}
.foot{{margin-top:auto;width:100%;display:flex;flex-direction:column;align-items:center;gap:12px}}
.live{{display:flex;align-items:center;gap:14px;background:rgba(7,21,40,.9);border:1px solid rgba(255,255,255,.2);border-radius:40px;padding:12px 30px;font-weight:700;font-size:28px}}
.dot{{width:16px;height:16px;border-radius:50%;background:#ff3b3b;box-shadow:0 0 14px #ff3b3b}}
.cred{{font-size:25px;color:rgba(255,255,255,.85)}} .cred b{{color:{t['acc']}}}
.brand{{font-size:22px;letter-spacing:3px;color:rgba(255,255,255,.55)}}
"""

def deco(t):
    return ('<div class=shade></div>'
            '<div class=flare style="left:-180px;top:-160px"></div><div class=flare style="right:-200px;top:-140px"></div>'
            '<div class=streak style="top:38%"></div><div class=streak style="top:41%;opacity:.25"></div>')

FOOT = ('<div class=foot><div class=live><span class=dot></span>Seguilo en vivo en app.overgrip.com.ar</div>'
        '<div class=cred>Torneo <b>@jpqpadelquilmes</b> · Resultados <b>@overgripapp</b></div>'
        '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')

def scoreboard(m, label):
    def sets(sc, mine):
        out = ""
        for s in sc.split():
            a, b = s.split("/")
            v, o = (a, b) if mine else (b, a)
            out += f'<div class="set{" won" if int(v) > int(o) else ""}">{v}</div>'
        return out
    return (f'<div class=sb><div class=hd><span>{label}</span><span>Final</span></div>'
            f'<div class="row w"><div class=tri></div><div class=nm>{m["g"]}</div>{sets(m["s"], True)}</div>'
            f'<div class=row><div class=tri></div><div class=nm>{m["p"]}</div>{sets(m["s"], False)}</div></div>')

def story_resultados(d):
    t = T[d.get("tema", "azul")]
    css = base_css(t, 1080, 1920, d.get("fondo", "red.webp")) + """
.wrap{padding:150px 70px 230px}.list{width:100%;display:flex;flex-direction:column;gap:18px;margin-top:40px}"""
    cards = "".join(scoreboard(m, m.get("tag", d.get("cat", ""))) for m in d["partidos"])
    body = (f'<div class=strip><div class=a>JPQ 4°</div><div class=b>{d["strip"]}</div></div>'
            f'<img class=logo style="margin-top:46px" src="data:image/png;base64,{gen.LOGO}">'
            f'<div class=metal style="font-size:124px;margin-top:22px">{d["titulo"]}</div>'
            f'<div class=list>{cards}</div>{FOOT}')
    return css, f'{deco(t)}<div class=wrap>{body}</div>'

def post_hype(d):
    t = T["azul"]
    css = base_css(t, 1080, 1350, d.get("fondo","hero.webp")) + f"""
.wrap{{padding:60px 60px 50px}}
.sed{{width:100%;display:flex;flex-direction:column;gap:12px;margin-top:34px}}
.sed div{{display:flex;justify-content:space-between;align-items:center;background:linear-gradient(90deg,rgba(7,21,40,.95),rgba(7,21,40,.6));border-left:6px solid {t['hot']};padding:14px 24px;font-family:BC;font-weight:800;font-style:italic;font-size:40px;text-transform:uppercase}}
.sed small{{font-family:B;font-style:normal;font-weight:600;font-size:22px;letter-spacing:3px;color:{t['acc']}}}
"""
    sedes = "".join(f'<div>{a}<small>{b}</small></div>' for a, b in d["sedes"])
    body = (f'<div class=strip><div class=a>JPQ 4°</div><div class=b>{d["strip"]}</div></div>'
            f'<img class=logo style="margin-top:34px;width:104px;height:104px" src="data:image/png;base64,{gen.LOGO}">'
            f'<div class=kick style="margin-top:14px">{d["kick"]}</div>'
            f'<div class=metal style="font-size:150px;margin-top:6px">{d["titulo"]}</div>'
            f'<div class=sed>{sedes}</div>{FOOT}')
    return css, f'{deco(t)}<div class=wrap>{body}</div>'

def story_pasaron(d):
    t = T[d.get("tema", "azul")]
    n = len(d["cats"])
    fs = 30 if n <= 3 else 27
    css = base_css(t, 1080, 1920, d.get("fondo", "red.webp")) + f"""
.wrap{{padding:140px 70px 230px}}.grp{{width:100%;display:flex;flex-direction:column;gap:18px;margin-top:34px}}
.ch{{display:grid;grid-template-columns:1fr 1fr;gap:4px 22px;padding:12px 20px}}
.ch span{{font-size:{fs}px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:10px}}
.ch span:before{{content:"";flex:none;border-left:11px solid {t['hot']};border-top:8px solid transparent;border-bottom:8px solid transparent}}
"""
    blk = "".join(
        f'<div class=sb><div class=hd><span>{c["cat"]}</span><span>{d.get("etiq","A cuartos")}</span></div>'
        '<div class=ch>' + "".join(f'<span>{p}</span>' for p in c["parejas"]) + '</div></div>'
        for c in d["cats"])
    body = (f'<div class=strip><div class=a>JPQ 4°</div><div class=b>{d["strip"]}</div></div>'
            f'<img class=logo style="margin-top:36px;width:104px;height:104px" src="data:image/png;base64,{gen.LOGO}">'
            f'<div class=metal style="font-size:{d.get("fs",112)}px;margin-top:18px">{d["titulo"]}</div>'
            f'<div class=grp>{blk}</div>{FOOT}')
    return css, f'{deco(t)}<div class=wrap>{body}</div>'

def render(jobs, out):
    out = pathlib.Path(out); out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for j in jobs:
            css, body = {"story_resultados": story_resultados, "post_hype": post_hype, "story_pasaron": story_pasaron}[j["tipo"]](j)
            H = 1350 if j["tipo"].startswith("post") else 1920
            pg = b.new_page(viewport={"width": 1080, "height": H})
            pg.set_content(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>")
            pg.wait_for_timeout(300); pg.screenshot(path=str(out / j["archivo"])); pg.close()
            print(out / j["archivo"])
        b.close()

if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
