import os, requests, random, urllib.parse

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")

termos = ["echo dot 5", "jbl go 4", "fire tv stick", "redmi note 13", "air fryer mondial", "caixa jbl boombox"]

def buscar():
    termo = random.choice(termos)
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={urllib.parse.quote(termo)}&limit=20&sort=sold_quantity_desc"
    print(f"Buscando 20 de: {termo}")
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    print(f"Status: {r.status_code}")
    if r.status_code!= 200:
        return None
    for item in r.json().get("results", [])[:10]:
        permalink = item.get("permalink","")
        if "produto.mercadolivre.com.br/MLB-" in permalink:
            base = permalink.split("?")[0]
            link = f"{base}?matt_tool=77761463&matt_word=matheus20190&forceInApp=true"
            return {"titulo": item["title"][:90], "preco": item["price"], "link": link, "img": item.get("thumbnail","").replace("-I.jpg","-O.jpg")}
    return None

def enviar(p):
    texto = f"🔥 OFERTA COM 20 ITENS TESTADOS 🔥\n\n📦 {p['titulo']}\n💰 R$ {p['preco']}\n\n👇 LINK DIRETO 👇\n{p['link']}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" if p.get("img") else f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CANAL, "photo": p.get("img"), "caption": texto} if p.get("img") else {"chat_id": CANAL, "text": texto}
    print(requests.post(url, data=data, timeout=15).text)

p = buscar()
if p:
    enviar(p)
    print("POSTOU 1 DOS 20")
else:
    print("API bloqueada aqui - no GitHub vai dar 200")
