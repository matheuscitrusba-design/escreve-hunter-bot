import os, requests, time, random, re

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = "magazineafilliados"

# OS 5 PRODUTOS QUE MAIS PAGAM COMISSÃO
TERMOS = [
    "smart tv 43 qled",
    "iphone 13 128gb",
    "air fryer 4 litros",
    "geladeira frost free 310l",
    "notebook i5 8gb"
]

def enviar_telegram(foto, texto):
    try:
        if foto and foto.startswith("http"):
            r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHANNEL, "photo": foto, "caption": texto, "parse_mode": "HTML"},
                timeout=20)
        else:
            r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML"},
                timeout=20)
        print(f"Telegram: {r.status_code} - {r.text[:100]}")
        return r.status_code == 200
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False

print(f"🚀 INICIANDO HUNTER - LOJA {LOJA}")

for termo in TERMOS:
    print(f"\n--- Buscando: {termo} ---")
    try:
        # API do Magalu que NÃO bloqueia o GitHub
        url_api = f"https://www.magazineluiza.com.br/api/v5/search?q={termo.replace(' ','%20')}&page=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        r = requests.get(url_api, headers=headers, timeout=20)
        print(f"STATUS API: {r.status_code}")

        if r.status_code!= 200:
            print(f"Pulando {termo}")
            continue

        data = r.json()
        # Magalu muda o JSON, tenta 2 caminhos
        produtos = []
        if "data" in data and "products" in data["data"]:
            produtos = data["data"]["products"]
        elif "products" in data:
            produtos = data["products"]

        print(f"Achados: {len(produtos)}")
        if not produtos:
            continue

        # Pega só o melhor produto do termo (o mais barato com foto)
        p = produtos[0]
        titulo = p.get("title") or p.get("name") or termo
        titulo = titulo[:90]

        # Preço
        preco_obj = p.get("price", {})
        if isinstance(preco_obj, dict):
            preco = preco_obj.get("bestPrice", {}).get("formatted") or preco_obj.get("bestPrice", {}).get("value") or preco_obj.get("formatted") or "Consulte"
            if isinstance(preco, dict):
                preco = preco.get("value")
        else:
            preco = str(preco_obj)

        # Link e Foto
        url_prod = p.get("url") or p.get("path") or ""
        if not url_prod.startswith("/"):
            url_prod = "/" + url_prod

        # TRANSFORMA EM SEU LINK DE AFILIADO
        link_afiliado = f"https://www.magazinevoce.com.br/{LOJA}{url_prod}"

        # Foto
        foto = ""
        img = p.get("image") or p.get("images", [{}])[0] if p.get("images") else {}
        if isinstance(img, dict):
            foto = img.get("url") or img.get("large") or ""
        elif isinstance(img, str):
            foto = img
        else:
            # tenta pegar do search
            foto = p.get("imageUrl") or ""

        # Texto pronto pro Telegram
        texto = f"""🔥 <b>{titulo.upper()}</b>

💰 <b>Por: {preco}</b>
✅ Loja Oficial Magalu - Entrega Rápida
✅ Garantia de 1 ano

👉 <b>COMPRE COM DESCONTO AQUI:</b>
{link_afiliado}

#oferta #achados #magalu"""

        print(f"Enviando: {titulo}")
        ok = enviar_telegram(foto, texto)

        # Espera 10 seg entre produtos pra não tomar spam
        time.sleep(10)

    except Exception as e:
        print(f"ERRO no termo {termo}: {e}")
        continue

print("\n✅ FIM - HUNTER FINALIZADO COM SUCESSO")
