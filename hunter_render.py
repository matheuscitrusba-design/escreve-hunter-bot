import os, re, time, random, requests
from flask import Flask
from datetime import datetime
app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = os.getenv("LOJA_MAGALU", "magazineafilliados")
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/122.0.0.0", "Accept-Language": "pt-BR"}
def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")
def buscar(termo):
    url = f"https://www.magazineluiza.com.br/busca/{termo.replace(' ','-')}/"
    try:
        html = requests.get(url, headers=HEADERS, timeout=20).text
        matches = re.findall(r'/p/([a-z0-9-]+)/([a-z0-9]{7,10})/', html)
        produtos=[]; vistos=set()
        for slug,code in matches:
            if code not in vistos and len(slug)>5:
                vistos.add(code); produtos.append({"slug":slug,"code":code,"title":slug.replace("-"," ").title()})
        log(f"{termo} -> {len(produtos)} achados | {len(html)} chars")
        return produtos[:5]
    except Exception as e:
        log(f"Erro {e}"); return []
def enviar(texto):
    r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":CHANNEL,"text":texto,"parse_mode":"HTML"}, timeout=20)
    return r.status_code==200
def rodar():
    termos=random.sample(["smart tv 43","air fryer","iphone","galaxy a54","caixa jbl","ventilador","fogao","geladeira","notebook","tenis nike"],4)
    env=0
    for termo in termos:
        if env>=3: break
        for p in buscar(termo):
            link=f"https://www.magazinevoce.com.br/{LOJA}/{p['slug']}/p/{p['code']}/"
            try:
                if "nao foi encontrado" in requests.get(link, headers=HEADERS, timeout=15).text.lower(): continue
            except: continue
            if enviar(f"🔥 <b>{p['title'].upper()}</b>\n\n👇 COMPRAR:\n{link}\n\n#oferta"):
                env+=1; time.sleep(8); break
    return env
@app.route("/")
def home(): return "Hunter ON"
@app.route("/hunt")
def hunt(): return f"Enviou {rodar()}"
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
