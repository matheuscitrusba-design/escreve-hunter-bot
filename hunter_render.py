import os, re, time, random, requests
from flask import Flask
app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = os.getenv("LOJA_MAGALU", "magazineafilliados")
HEADERS = {"User-Agent":"Mozilla/5.0","Accept-Language":"pt-BR"}

def enviar(t):
    try:
        r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":CHANNEL,"text":t,"parse_mode":"HTML"}, timeout=20)
        return r.status_code==200
    except: return False

def rodar():
    termos=["smart-tv-43","air-fryer","iphone","jbl","ventilador","notebook"]
    random.shuffle(termos)
    env=0
    for termo in termos[:4]:
        if env>=3: break
        try:
            url=f"https://www.magazinevoce.com.br/{LOJA}/busca/{termo}/"
            html=requests.get(url, headers=HEADERS, timeout=20).text
            # pega qualquer produto /p/slug/codigo/
            prods=re.findall(r'/p/([a-z0-9\-]+)/([a-z0-9]{7,})/', html)
            vistos=set()
            for slug,code in prods:
                if code in vistos or len(slug)<4: continue
                vistos.add(code)
                link=f"https://www.magazinevoce.com.br/{LOJA}/{slug}/p/{code}/"
                titulo=slug.replace("-"," ").title()
                txt=f"🔥 <b>{titulo}</b>\n\n💰 OFERTA MAGALU\n👇 LINK COM DESCONTO:\n{link}\n\n#oferta #{termo}"
                if enviar(txt):
                    env+=1
                    time.sleep(5)
                    break
        except Exception as e:
            print(e)
            continue
    return env

@app.route("/")
def home(): return "Hunter ON - Magazine Voce"
@app.route("/hunt")
def hunt(): return f"Enviou {rodar()}"
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
