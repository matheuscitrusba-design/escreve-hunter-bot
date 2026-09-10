import os, requests, time, urllib.parse

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
BASE_PROXY = "https://silent-math-e8e3.matheuscitrusba.workers.dev/?url="
ml_url = "https://api.mercadolibre.com/sites/MLB/search?q=oferta&limit=20&sort=price_asc"
full_url = BASE_PROXY + urllib.parse.quote(ml_url, safe='')

print(f"Tentando: {full_url}")
r = requests.get(full_url, timeout=30)
print(f"STATUS: {r.status_code}")
items = r.json().get("results", [])
print(f"ACHADOS: {len(items)}")

for item in items:
    title = item["title"]
    price = item["price"]
    link = item["permalink"]
    thumb = item["thumbnail"].replace("http://","https://")
    texto = f"🔥 {title}\n💰 R$ {price}\n\n👉 {link}"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(api_url, data={"chat_id": CHANNEL, "photo": thumb, "caption": texto}, timeout=20)
    print(f"ENVIADO: {title[:40]}")
    time.sleep(2)
