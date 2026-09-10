import os, requests, time, urllib.parse, json

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

original_url = "https://api.mercadolibre.com/sites/MLB/search?q=oferta&limit=20&sort=price_asc"

# Lista de proxies pra tentar furar o bloqueio
proxies_to_try = [
    original_url,
    f"https://corsproxy.io/?{urllib.parse.quote(original_url, safe='')}",
    f"https://api.codetabs.com/v1/proxy/?quest={original_url}",
    f"https://thingproxy.freeboard.name/fetch?url={original_url}"
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

items = []
for proxy_url in proxies_to_try:
    try:
        print(f"Tentando: {proxy_url[:80]}...")
        r = requests.get(proxy_url, headers=headers, timeout=25)
        print(f"STATUS: {r.status_code}")
        if r.status_code != 200:
            continue
        
        data = r.json()
        # Alguns proxies embrulham o json
        if "results" not in data and isinstance(data, dict) and "contents" in data:
            data = json.loads(data["contents"])
        
        if "results" in data and len(data["results"]) > 0:
            items = data["results"]
            print(f"DEU CERTO! ACHADOS: {len(items)}")
            break
    except Exception as e:
        print(f"Falhou: {e}")
        continue

if not items:
    print("ACHADOS: 0 produtos - todos os proxies falharam")
    exit(0)

print(f"ACHADOS: {len(items)} produtos")

for item in items[:20]:
    try:
        title = item["title"]
        price = item["price"]
        link = item["permalink"]
        thumb = item["thumbnail"].replace("http://", "https://")
        texto = f"🔥 {title}\n💰 R$ {price}\n\n👉 {link}"
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        resp = requests.post(api_url, data={"chat_id": CHANNEL, "photo": thumb, "caption": texto}, timeout=20)
        print(f"ENVIADO: {title[:40]} -> {resp.status_code}")
        time.sleep(2)
    except Exception as e:
        print(f"ERRO no item: {e}")
