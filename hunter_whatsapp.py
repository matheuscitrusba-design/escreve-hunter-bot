import os, requests, random, urllib.parse, json

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190"

def produto_vivo(permalink):
    # Testa se o produto realmente existe
    try:
        base = permalink.split("?")[0]
        if "/social/" in base or "/p/MLB" in base or "lista." in base:
            return False
        r = requests.get(base, timeout=12, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        # Se caiu em lista ou "não encontramos"
        if "lista.mercadolivre" in r.url or "Não encontramos nenhum anúncio" in r.text or r.status_code >= 400:
            print(f"MORTO: {base} -> {r.url[:80]}")
            return False
        print(f"VIVO: {base}")
        return True
    except:
        return False

def buscar():
    print(f"Hunter V6.0 - SÓ VIVOS - {ML_WORD}")
    termos = ["echo dot 5 alexa", "jbl go 4", "redmi note 13", "air fryer philips walita"]
    termo = random.choice(termos)
    url_ml = f"https://api.mercadolibre.com/sites/MLB/search?q={urllib.parse.quote(termo)}&limit=20&sort=sold_quantity_desc"

    # Usa proxy pra furar o 403 do Render
    for proxy_url in [
        f"https://api.allorigins.win/get?url={urllib.parse.quote(url_ml, safe='')}",
        f"https://api.codetabs.com/v1/proxy/?quest={urllib.parse.quote(url_ml, safe='')}",
    ]:
        try:
            print(f"Tentando: {proxy_url[:60]}")
            r = requests.get(proxy_url, timeout=20)
            if r.status_code!= 200:
                continue

            data = r.json()
            if "contents" in data: # allorigins
                data = json.loads(data["contents"])

            for item in data.get("results", []):
                permalink = item.get("permalink","")
                if "produto.mercadolivre.com.br/MLB-" in permalink:
                    if produto_vivo(permalink):
                        link_aff = f"{permalink.split('?')[0]}?matt_tool={ML_TOOL}&matt_word={ML_WORD}&matt_source=telegram_v6&forceInApp=true"
                        return {
                            "titulo": item["title"][:90],
                            "preco": item["price"],
                            "link": link_aff,
                            "img": item.get("thumbnail","").replace("-I.jpg","-O.jpg")
                        }
        except Exception as e:
            print(f"Erro: {e}")
            continue
    print("Nenhum vivo achado agora")
    return None

def enviar(prod):
    texto = f"🔥 PRODUTO VIVO TESTADO 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👇 LINK DIRETO SEM LISTA 👇\n{prod['link']}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" if prod.get("img") else f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CANAL, "photo": prod["img"], "caption": texto} if prod.get("img") else {"chat_id": CANAL, "text": texto}
    r = requests.post(url, data=data, timeout=20)
    print(f"Telegram: {r.text[:200]}")

p = buscar()
if p:
    enviar(p)
