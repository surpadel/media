import gen, premier
from playwright.sync_api import sync_playwright
t=gen.THEMES['azul']; r=gen.THEMES['rosa']
cab=[("2da","Covucci / Vélez","7/5 6/1"),("3ra","Cattaneo / Huenchuquir","7/5 1/6 6/3"),("4ta","Reynoso / Sacarelo","2/6 6/3 6/2"),
("5ta","Aristimuño / Cavazzoni","6/4 6/2"),("5ta +40","Castillo / Marcote","6/4 7/5"),("6ta","Aguilar / Isasi","6/1 7/6"),
("6ta +35","Peter / Torres","2/6 6/1 6/3"),("7ma","Borras / Roberts","2/6 6/1 7/6"),("7ma +40","Casalini / Fermoselle","6/2 6/3")]
dam=[("3ra","Amarillo / Miranda","6/3 5/7 6/2"),("4ta","Arrechea / Refort","6/1 4/6 6/2"),("5ta","Chapuis / Velázquez","6/2 7/5"),
("6ta","Boveri Ansaldo / Palena","5/7 6/3 6/2"),("7ma","Orellana / Yaniri","6/2 7/6")]
css=premier.base_css(t,1080,1350,"fondos/fondo-14-campeones-confeti.jpg")+f"""
.wrap{{padding:46px 48px 38px}}
.cols{{width:100%;display:flex;flex-direction:column;gap:14px;margin-top:22px}}
.grp .hd{{display:flex;justify-content:space-between;padding:6px 16px;font-weight:700;font-size:19px;letter-spacing:3px;text-transform:uppercase}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
.it{{display:flex;align-items:center;gap:12px;padding:7px 14px;border-top:1px solid rgba(255,255,255,.08)}}
.it .c{{width:92px;flex:none;font-family:BC;font-weight:800;font-style:italic;font-size:26px;text-transform:uppercase}}
.it .n{{flex:1;min-width:0}} .it .p{{font-size:23px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.it .s{{font-size:16px;color:rgba(255,255,255,.6);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.pend .p{{color:rgba(255,255,255,.7);font-style:italic}}
.foot .live{{font-size:24px;padding:9px 24px}} .cred{{font-size:22px}} .brand{{font-size:19px}}
"""
def grp(title,items,col,bg):
    rows="".join(f'<div class="it{" pend" if n=="Final en juego" else ""}"><div class=c style="color:{col}">{c}</div><div class=n><div class=p>{"🏆 " if n!="Final en juego" else ""}{n}</div><div class=s>{s}</div></div></div>' for c,n,s in items)
    return f'<div class="sb grp"><div class=hd style="background:{bg}"><span>{title}</span><span>Campeones</span></div><div class=grid>{rows}</div></div>'
body=(f'<div class=strip><div class=a>JPQ 4°</div><div class=b>Abierto · Quilmes · Finales</div></div>'
 f'<div class=metal style="font-size:104px;margin-top:20px">Los <span class=gold>campeones</span></div>'
 f'<div class=cols>{grp("Caballeros",cab,t["hot"],f"linear-gradient(90deg,{t[chr(99)+chr(111)+chr(117)+chr(114)+chr(116)+chr(50)]},{t[chr(99)+chr(111)+chr(117)+chr(114)+chr(116)]})")}'
 f'{grp("Damas",dam,r["hot"],f"linear-gradient(90deg,{r[chr(99)+chr(111)+chr(117)+chr(114)+chr(116)+chr(50)]},{r[chr(99)+chr(111)+chr(117)+chr(114)+chr(116)]})")}</div>{premier.FOOT}')
html=f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{premier.deco(t)}<div class=wrap>{body}</div></body></html>"
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1080,"height":1350})
    pg.set_content(html); pg.wait_for_timeout(400); pg.screenshot(path="out/jpq-post-campeones-v2.png"); b.close()
print("ok")
