import os, requests, time, urllib.parse, json

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = "magazineafilliados"

TERMOS = ["smart tv 43 qled", "iphone 13 128gb", "air fryer"]

def fetch_com_proxy(url_alvo):
    """Tenta buscar passando por 3 proxies diferentes"""
    proxies = [
        url_alvo,
        f"https://corsproxy.io/?{urllib.parse.quote(url_alvo)}",
        f"https://api.allorigins.win/raw?url={urllib.parse.quote(url_alvo)}",
        f"https://api.codetabs.com/v1/proxy?quest={urllib.parse.quote(url_alvo)}"
    ]
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    for p_url in proxies:
        try:
            print(f" Tentando proxy: {p_url[:70]}...")
            r = requests.get(p_url, headers=headers, timeout=20)
            print(f" -> STATUS: {r.status_code}")
            if r.status_code == 200 and len(r.text) > 500:
                try:
                    # allorigins retorna texto puro, codetabs json
                    data = r.json()
                    # Se veio embrulhado
                    if "contents" in data:
                        return json.loads(data["contents"])
                    return data
                except:
                    # Se o proxy retornou JSON direto mas em texto
                    return json.loads(r.text)
        except Exception as e:
            print(f" -> Falhou: {e}")
    return None

def enviar(foto, texto):
    try:
        if foto:
            r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHANNEL, "photo": foto, "caption": texto, "parse_mode": "HTML"}, timeout=20)
        else:
            r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML"}, timeout=20)
        print(f"Telegram: {r.status_code}")
        return True
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False

print(f"🚀 HUNTER COM PROXY - LOJA {LOJA}")

achou_algum = False

for termo in TERMOS:
    print(f"\n--- {termo} ---")
    url_api = f"https://www.magazineluiza.com.br/api/v5/search?q={termo.replace(' ','%20')}"

    data = fetch_com_proxy(url_api)
    if not data:
        print(" Nenhum proxy funcionou pra esse termo")
        continue

    produtos = []
    if "data" in data and "products" in data["data"]:
        produtos = data["data"]["products"]
    elif "products" in data:
        produtos = data["products"]

    if not produtos:
        continue

    p = produtos[0]
    titulo = (p.get("title") or termo)[:90]
    preco = p.get("price", {})
    if isinstance(preco, dict):
        preco = preco.get("bestPrice", {}).get("formatted") or str(preco.get("bestPrice", {}).get("value") or "Oferta")
    url_prod = p.get("url") or ""
    link_afiliado = f"https://www.magazinevoce.com.br/{LOJA}{url_prod}"

    img = p.get("image", "")
    foto = img.get("url") if isinstance(img, dict) else img

    texto = f"""🔥 <b>{titulo.upper()}</b>
💰 <b>{preco}</b>
👉 {link_afiliado}"""

    enviar(foto, texto)
    achou_algum = True
    time.sleep(5)

# PLANO B: Se TODOS os proxies falharem, manda 3 produtos fixos SEUS pra não ficar vazio
if not achou_algum:
    print("TUDO BLOQUEADO - ATIVANDO PLANO B COM SEUS LINKS")
    fallback = [
        ("TV 43 TCL QLED 43S5K - R$1.484 no Pix", "https://www.magazinevoce.com.br/magazineafilliados/tv-43-tcl-full-hd-qled-43s5k-google-tv-2-hdmi/p/240424200/et/tves/", "https://a-static.mlcdn.com.br/800x560/tv-43-tcl-full-hd-qled-43s5k/magazineluiza/240424200/43s5k.jpg"),
        ("iPhone 13 128GB - Mais vendido", "https://www.magazinevoce.com.br/magazineafilliados/busca/?q=iphone+13", ""),
        ("Air Fryer Mondial 4L", "https://www.magazinevoce.com.br/magazineafilliados/busca/?q=air+fryer", "")
    ]
    for tit, link, foto in fallback:
        enviar(foto, f"🔥 {tit}\n💰 Oferta Magalu\n👉 {link}")
        time.sleep(3)

print("✅ FIM")
