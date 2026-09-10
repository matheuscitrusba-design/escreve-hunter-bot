import os, requests, random, urllib.parse, json

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190"

def buscar():
    print(f"Hunter V7 GitHub - {ML_WORD}")
    termo = random.choice(["echo dot 5 alexa", "jbl go 4", "fire tv stick", "redmi note 13", "air fryer mondial"])
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={urllib.parse.quote(termo)}&limit=20&sort=sold_quantity_desc"
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (GitHub Actions)"})
    print(f"API status: {r.status_code}")
    if r.status_code!= 200:
        return None
    for item in r.json().get("results", []):
        permalink = item.get("permalink","")
        if "produto.mercadolivre.com.br/MLB-" in permalink:
            base = permalink.split("?")[0]
            link_aff = f"{base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}&forceInApp=true"
            print(f"VIVO: {item['title'][:60]}")
            return {"titulo": item["title"][:90], "preco": item["price"], "link": link_aff, "img": item.get("thumbnail","").replace("-I.jpg","-O.jpg")}
    return None

def enviar(prod):
    texto = f"🔥 OFERTA ACHADA 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👇 LINK DIRETO COM SEU DESCONTO 👇\n{prod['link']}"
    if prod.get("img"):
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CANAL, "photo": prod["img"], "caption": texto}, timeout=20)
    else:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CANAL, "text": texto}, timeout=15)

p = buscar()
if p:
    enviar(p)
    print("Postado com sucesso - produto vivo")
