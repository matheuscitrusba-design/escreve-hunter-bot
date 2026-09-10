import os, requests, time, urllib.parse

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

# URL original do ML
original_url = "https://api.mercadolibre.com/sites/MLB/search?q=oferta_do_dia&limit=20&sort=price_asc"
# Passa por um proxy pra não tomar 403 do GitHub
url = f"https://api.allorigins.win/raw?url={urllib.parse.quote(original_url, safe='')}"

headers = {"User-Agent": "Mozilla/5.0"}

print(f"Tentando: {url}")
r = requests.get(url, headers=headers, timeout=30)
print(f"STATUS: {r.status_code}")

try:
    data = r.json()
    # Se veio pelo allorigins, as vezes vem dentro de outra estrutura
    if "results" not in data and "contents" in data:
        import json
        data = json.loads(data["contents"])
    
    items = data.get("results", [])
    print(f"ACHADOS: {len(items)} produtos")

    for item in items[:20]:
        title = item["title"]
        price = item["price"]
        link = item["permalink"]
        thumb = item["thumbnail"].replace("http://", "https://")
        
        texto = f"🔥 {title}\n💰 R$ {price}\n\n👉 {link}"
        
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        resp = requests.post(api_url, data={"chat_id": CHANNEL, "photo": thumb, "caption": texto}, timeout=20)
        print(f"ENVIADO: {title[:40]} -> {resp.status_code} {resp.text[:100]}")
        time.sleep(2)

except Exception as e:
    print(f"ERRO GERAL: {e}")
    print(r.text[:1000])
