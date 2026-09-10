import os, requests, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

# Usa um proxy que o Mercado Livre não bloqueia
url = "https://api.allorigins.win/raw?url=https://api.mercadolibre.com/sites/MLB/search?q=celular&limit=10"

print(f"Tentando: {url}")
r = requests.get(url, timeout=30)
print(f"STATUS: {r.status_code}")

data = r.json()
items = data.get("results", [])
print(f"ACHADOS: {len(items)}")

for item in items[:5]:
    title = item["title"]
    price = item["price"]
    link = item["permalink"]
    thumb = item["thumbnail"].replace("http://","https://")
    texto = f"🔥 {title}\n💰 R$ {price}\n\n👉 {link}"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    res = requests.post(api_url, data={"chat_id": CHANNEL, "photo": thumb, "caption": texto}, timeout=20)
    print(f"ENVIADO: {title[:40]} - {res.status_code}")
    time.sleep(2)
