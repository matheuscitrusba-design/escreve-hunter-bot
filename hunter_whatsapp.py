import os, requests, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

headers = {"User-Agent": "Mozilla/5.0"}

url = "https://api.mercadolibre.com/sites/MLB/search?q=oferta+do+dia&limit=20"
r = requests.get(url, headers=headers, timeout=20)
print(f"STATUS: {r.status_code}")

items = r.json().get("results", [])
print(f"ACHADOS: {len(items)} produtos")

for item in items[:20]:
    try:
        title = item["title"]
        price = item["price"]
        link = item["permalink"]
        thumb = item["thumbnail"]
        texto = f"🔥 {title}\n💰 R$ {price}\n\n👉 {link}"
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        requests.post(api_url, data={"chat_id": CHANNEL, "photo": thumb, "caption": texto}, timeout=20)
        print(f"ENVIADO: {title[:40]}")
        time.sleep(2)
    except Exception as e:
        print(f"ERRO: {e}")
