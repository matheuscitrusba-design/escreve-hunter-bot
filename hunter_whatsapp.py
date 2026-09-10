import os, requests, time, urllib.parse, json

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
BASE_PROXY = "https://silent-math-e8e3.matheuscitrusba.workers.dev/?url="

# Mudei para um termo que SEMPRE retorna: celular
ml_url = "https://api.mercadolibre.com/sites/MLB/search?q=celular&limit=10"
full_url = BASE_PROXY + urllib.parse.quote(ml_url, safe='')

print(f"Tentando: {full_url}")
r = requests.get(full_url, timeout=30)
print(f"STATUS: {r.status_code}")

try:
    data = r.json()
    print(f"KEYS: {data.keys()}")
    items = data.get("results", [])
    print(f"ACHADOS: {len(items)}")
    if len(items) == 0:
        print(f"RESPOSTA CRUA: {r.text[:500]}")
except Exception as e:
    print(f"ERRO JSON: {e}")
    print(r.text[:500])
    items = []

for item in items:
    title = item["title"]
    price = item["price"]
    link = item["permalink"]
    thumb = item["thumbnail"].replace("http://","https://")
    texto = f"🔥 {title}\n💰 R$ {price}\n\n👉 {link}"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    res = requests.post(api_url, data={"chat_id": CHANNEL, "photo": thumb, "caption": texto}, timeout=20)
    print(f"ENVIADO: {title[:40]} - {res.status_code}")
    time.sleep(2)
