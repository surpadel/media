import base64, json, os, sys, pathlib
from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).parent
F = pathlib.Path(os.environ.get("FONTS_DIR", D / "node_modules/@fontsource"))

def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

FONTS = f"""
@font-face{{font-family:BC;font-weight:700;font-style:italic;src:url(data:font/woff2;base64,{b64(F/'barlow-condensed/files/barlow-condensed-latin-700-italic.woff2')})}}
@font-face{{font-family:BC;font-weight:800;font-style:italic;src:url(data:font/woff2;base64,{b64(F/'barlow-condensed/files/barlow-condensed-latin-800-italic.woff2')})}}
@font-face{{font-family:B;font-weight:400;src:url(data:font/woff2;base64,{b64(F/'barlow/files/barlow-latin-400-normal.woff2')})}}
@font-face{{font-family:B;font-weight:600;src:url(data:font/woff2;base64,{b64(F/'barlow/files/barlow-latin-600-normal.woff2')})}}
@font-face{{font-family:B;font-weight:700;src:url(data:font/woff2;base64,{b64(F/'barlow/files/barlow-latin-700-normal.woff2')})}}
"""
LOGO = b64(os.environ.get("LOGO_PNG", D / "logo.png"))

THEMES = {
    "azul": dict(bg1="#071528", bg2="#0b1d36", court="#1d5cad", court2="#174d94", acc="#74b4e8", hot="#f2b21c"),
    "rosa": dict(bg1="#16071a", bg2="#2a0e27", court="#b8366f", court2="#8f2a5c", acc="#f4a3c4", hot="#ff6fa8"),
}

def css(t):
    return FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:B;color:#fff;
 background:radial-gradient(ellipse 900px 520px at 50% -80px,rgba(255,255,255,.22),transparent 70%),
 linear-gradient(180deg,{t['bg1']} 0%,{t['bg2']} 55%,{t['bg1']} 100%);position:relative}}
.spot{{position:absolute;top:60px;width:160px;height:40px;border-radius:20px;background:rgba(255,255,255,.85);filter:blur(10px)}}
.beam{{position:absolute;top:70px;width:520px;height:1100px;background:linear-gradient(180deg,rgba(255,255,255,.10),transparent 80%);filter:blur(6px)}}
.floor{{position:absolute;left:-200px;right:-200px;bottom:0;height:520px;
 background:linear-gradient(180deg,{t['court2']},{t['court']} 40%,{t['bg1']});
 transform:perspective(700px) rotateX(48deg);transform-origin:bottom;opacity:.55}}
.line{{position:absolute;left:50%;bottom:0;width:10px;height:360px;margin-left:-5px;
 background:linear-gradient(0deg,rgba(255,255,255,.75),transparent);transform:perspective(700px) rotateX(48deg);transform-origin:bottom}}
.stars{{position:absolute;right:90px;top:330px;opacity:.35}}
.stars i{{position:absolute;color:{t['acc']};font-style:normal;font-size:22px}}
.wrap{{position:absolute;inset:0;padding:200px 80px 250px;display:flex;flex-direction:column;align-items:center}}
.logo{{width:170px;height:170px}}
.kick{{margin-top:22px;font-family:B;font-weight:700;letter-spacing:6px;font-size:28px;color:{t['acc']};text-transform:uppercase}}
h1{{font-family:BC;font-weight:800;font-style:italic;font-size:118px;line-height:.92;text-transform:uppercase;text-align:center;margin-top:10px}}
h1 em{{color:{t['hot']};font-style:italic}}
.cat{{margin-top:22px;padding:10px 30px;border:3px solid {t['acc']};border-radius:40px;font-family:BC;font-weight:700;font-style:italic;font-size:44px;text-transform:uppercase}}
.list{{margin-top:44px;width:100%;display:flex;flex-direction:column;gap:20px}}
.m{{background:rgba(7,21,40,.62);border:2px solid rgba(255,255,255,.12);border-left:8px solid {t['acc']};border-radius:18px;padding:20px 28px;display:flex;align-items:center;gap:20px}}
.m .who{{flex:1;min-width:0}}
.m .tag{{font-size:22px;letter-spacing:3px;font-weight:700;color:{t['acc']};text-transform:uppercase;margin-bottom:6px}}
.w{{font-weight:700;font-size:36px;line-height:1.15}}
.w b{{color:{t['hot']}}}
.l{{font-size:28px;color:rgba(255,255,255,.62);margin-top:4px}}
.sc{{font-family:BC;font-weight:800;font-style:italic;font-size:46px;color:{t['hot']};white-space:nowrap;text-align:right}}
.champ{{margin-top:60px;width:100%;text-align:center;background:rgba(7,21,40,.6);border:3px solid {t['hot']};border-radius:28px;padding:50px 40px}}
.trophy{{font-size:110px;line-height:1}}
.champ .names{{font-family:BC;font-weight:800;font-style:italic;font-size:92px;line-height:1;text-transform:uppercase;margin-top:20px}}
.champ .sub{{font-size:30px;color:rgba(255,255,255,.7);margin-top:26px}}
.champ .score{{font-family:BC;font-weight:800;font-style:italic;font-size:70px;color:{t['hot']};margin-top:8px}}
.model{{position:absolute;top:120px;left:50%;transform:translateX(-50%) rotate(-4deg);background:#e23;color:#fff;font-weight:700;font-size:30px;padding:8px 26px;border-radius:8px;letter-spacing:4px}}
.tl{{margin-top:50px;width:100%;display:flex;flex-direction:column;gap:22px}}
.st{{display:flex;align-items:center;gap:28px;background:rgba(7,21,40,.62);border:2px solid rgba(255,255,255,.12);border-radius:20px;padding:24px 32px}}
.st .n{{width:74px;height:74px;border-radius:50%;border:4px solid {t['hot']};display:flex;align-items:center;justify-content:center;font-family:BC;font-weight:800;font-style:italic;font-size:40px;color:{t['hot']};flex:none}}
.st .tx{{flex:1}} .st .a{{font-family:BC;font-weight:800;font-style:italic;font-size:58px;line-height:1;text-transform:uppercase}}
.st .b{{font-size:28px;color:{t['acc']};font-weight:600;margin-top:4px}}
.lead{{margin-top:26px;font-size:34px;text-align:center;color:rgba(255,255,255,.85);line-height:1.3}}
.grp{{margin-top:34px;width:100%;display:flex;flex-direction:column;gap:22px}}
.blk{{background:rgba(7,21,40,.62);border:2px solid rgba(255,255,255,.12);border-left:8px solid {t['acc']};border-radius:18px;padding:18px 26px}}
.blk .tag{{font-family:BC;font-weight:800;font-style:italic;font-size:40px;text-transform:uppercase;color:{t['hot']};margin-bottom:8px}}
.chips{{display:grid;grid-template-columns:1fr 1fr;gap:6px 24px}}
.chips span{{font-size:27px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.foot{{margin-top:auto;padding-top:30px;text-align:center}}
.compact .m{{padding:14px 26px}} .compact .w{{font-size:33px}} .compact .l{{font-size:26px}} .compact .sc{{font-size:42px}} .compact h1{{font-size:104px}} .compact .list{{margin-top:32px;gap:16px}}
.foot .live{{display:inline-block;background:{t['hot']};color:{t['bg1']};font-weight:700;font-size:30px;padding:14px 34px;border-radius:40px}}
.foot .cred{{margin-top:22px;font-size:27px;color:rgba(255,255,255,.85)}}
.foot .cred b{{color:{t['acc']}}}
.foot .brand{{margin-top:14px;font-size:24px;letter-spacing:2px;color:rgba(255,255,255,.55)}}
"""

POS={'hero.webp':'center','cesped.webp':'35% center','red.webp':'30% center'}

def shell(t, inner, model=False, compact=False, fondo=None):
    stars = "".join(f'<i style="left:{x}px;top:{y}px">★</i>' for x, y in [(0,0),(40,60),(-30,95),(10,150)])
    extra = ''
    if fondo:
        extra = (f'.floor,.line,.beam,.spot{{display:none}}'
                 f'body{{background:linear-gradient(180deg,rgba(7,21,40,.93) 0%,rgba(7,21,40,.6) 25%,rgba(7,21,40,.55) 50%,rgba(7,21,40,.8) 78%,rgba(7,21,40,.97) 100%),url(data:image/webp;base64,{b64(D/fondo)}) {POS.get(fondo,"center")}/cover!important}}'
                 '.m,.blk,.st{backdrop-filter:blur(8px)} h1,.lead{text-shadow:0 3px 14px rgba(0,0,0,.8)}')
    return f"""<html><head><meta charset=utf-8><style>{css(t)}{extra}</style></head><body>
<div class=beam style="left:-80px;transform:rotate(-18deg)"></div><div class=beam style="right:-80px;transform:rotate(18deg)"></div>
<div class=spot style="left:120px"></div><div class=spot style="right:120px"></div>
<div class=floor></div><div class=line></div><div class=stars>{stars}</div>
{'<div class=model>MODELO</div>' if model else ''}
<div class="wrap{' compact' if compact else ''}"><img class=logo src="data:image/png;base64,{LOGO}">{inner}<div class=foot><div class=live>Seguilo en vivo en app.overgrip.com.ar</div>
<div class=cred>Torneo <b>@jpqpadelquilmes</b> · Resultados <b>@overgripapp</b></div>
<div class=brand>@surpadelstore · surpadel.com.ar</div></div></div></body></html>"""

def resultados(d, t):
    rows = "".join(
        f'<div class=m><div class=who><div class=tag>{m.get("tag","")}</div>'
        f'<div class=w><b>{d.get("icono","✓")}</b> {m["g"]}</div><div class=l>{m["p"]}</div></div><div class=sc>{m["s"]}</div></div>'
        for m in d["partidos"])
    inner = f'<div class=kick>{d["kick"]}</div><h1>{d["titulo"]}</h1>'
    if d.get("cat"): inner += f'<div class=cat>{d["cat"]}</div>'
    return shell(t, inner + f'<div class=list>{rows}</div>', model=d.get('modelo',False), compact=len(d['partidos'])>4, fondo=d.get('fondo'))

def campeones(d, t):
    inner = (f'<div class=kick>{d["kick"]}</div><h1>¡Tenemos<br><em>campeones!</em></h1>'
             f'<div class=cat>{d["cat"]}</div>'
             f'<div class=champ><div class=trophy>🏆</div><div class=names>{d["g"]}</div>'
             f'<div class=sub>Final vs. {d["p"]}</div><div class=score>{d["s"]}</div></div>')
    return shell(t, inner, model=d.get("modelo", False))

def agenda(d, t):
    st = "".join(f'<div class=st><div class=n>{i+1}</div><div class=tx><div class=a>{a}</div><div class=b>{b}</div></div></div>' for i,(a,b) in enumerate(d["etapas"]))
    inner = f'<div class=kick>{d["kick"]}</div><h1>{d["titulo"]}</h1><div class=lead>{d["lead"]}</div><div class=tl>{st}</div>'
    return shell(t, inner, fondo=d.get('fondo'))

def pasaron(d, t):
    blk = "".join(f'<div class=blk><div class=tag>{c["cat"]}</div><div class=chips>' + "".join(f'<span>{p}</span>' for p in c["parejas"]) + '</div></div>' for c in d["cats"])
    inner = f'<div class=kick>{d["kick"]}</div><h1>{d["titulo"]}</h1>'
    if d.get("sub"): inner += f'<div class=cat>{d["sub"]}</div>'
    return shell(t, inner + f'<div class=grp>{blk}</div>', model=d.get("modelo",False), compact=True, fondo=d.get('fondo'))

def render(jobs, out):
    out = pathlib.Path(out); out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for j in jobs:
            t = THEMES[j.get("tema", "azul")]
            html = {"resultados": resultados, "campeones": campeones, "agenda": agenda, "pasaron": pasaron}[j["tipo"]](j, t)
            pg.set_content(html); pg.wait_for_timeout(300)
            pg.screenshot(path=str(out / j["archivo"]))
            print(out / j["archivo"])
        b.close()

if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
