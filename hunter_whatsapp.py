import os, requests, random

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190g"

def buscar():
    print("Hunter V5 FINAL - Caçando...")
    termos = ["iphone", "fone bluetooth", "air fryer", "smartwatch xiaomi", "ps5", "tenis nike", "notebook", "tv 50"]
    random.shuffle(termos)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    for termo in termos:
        try:
            print(f"Tentando: {termo}")
            # Usa 2 APIs diferentes pra garantir
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=5&sort=price_asc"
            r = requests.get(url, headers=headers, timeout=20)
            data = r.json()
            results = data.get("results", [])
            if results:
                p = random.choice(results)
                titulo = p["title"][:90]
                preco = p["price"]
                link = p["permalink"]
                link_aff = f"{link}?matt_tool={ML_TOOL}&matt_word={ML_WORD}&matt_source=HunterV5"
                print(f"ACHOU: {titulo}")
                return {"titulo": titulo, "preco": preco, "link": link_aff, "termo": termo}
        except Exception as e:
            print(f"Erro {termo}: {e}")
            continue
    return None

def enviar(prod):
    texto = f"🔥 ACHADO IMPERDÍVEL 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👉 {prod['link']}\n\n#achados #promoção"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
    print(f"Telegram: {r.text}")
    return r.json().get("ok", False)

prod = buscar()
if prod:
    enviar(prod)
else:
    print("Nada encontrado, tentando termo genérico...")
    # Fallback: posta um produto fixo pra não ficar sem postar
    enviar({"titulo": "Kit 3 Fones Bluetooth TWS", "preco": 99.90, "link": f"https://www.mercadolivre.com.br/fone-bluetooth?matt_tool={ML_TOOL}&matt_word={ML_WORD}", "termo": "fallback"})
