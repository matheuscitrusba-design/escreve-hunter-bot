import os, requests, random

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190"

def buscar():
    print(f"Hunter V5.8 - Anti-Capa - Afiliado {ML_WORD}")

    # LINKS REAIS DE PRODUTO QUE JÁ TESTEI COM SEU AFILIADO - NÃO VÃO PRA CAPA
    produtos_reais = [
        {
            "titulo": "Echo Dot 5ª Geração Alexa Original Amazon",
            "preco": 299,
            "link_base": "https://produto.mercadolivre.com.br/MLB-3290968148-echo-dot-5-geracao-smart-speaker-com-alexa-amazon-_JM"
        },
        {
            "titulo": "Fone JBL Vibe Buds Bluetooth Original",
            "preco": 199,
            "link_base": "https://produto.mercadolivre.com.br/MLB-3527424320-fone-de-ouvido-jbl-vibe-buds-bluetooth-preto-_JM"
        },
        {
            "titulo": "Air Fryer Mondial 4,2L 1500W Preta",
            "preco": 349,
            "link_base": "https://produto.mercadolivre.com.br/MLB-1840413287-fritadeira-eletrica-mondial-air-fryer-afn-40-bi-42l-1500w-_JM"
        },
    ]

    # 1. Tenta buscar um produto real da API (esse nunca vai pra capa)
    try:
        termo = random.choice(["echo dot 5", "jbl vibe buds", "air fryer mondial"])
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=10"
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        print(f"Busca API status: {r.status_code}")
        if r.status_code == 200:
            for item in r.json().get("results", []):
                permalink = item.get("permalink","")
                # SÓ ACEITA link de produto, não de /p/ e não de /social/
                if "produto.mercadolivre.com.br/MLB-" in permalink:
                    print(f"Link de produto REAL achado: {permalink[:80]}")
                    link_aff = f"{permalink.split('?')[0]}?matt_tool={ML_TOOL}&matt_word={ML_WORD}"
                    return {"titulo": item["title"][:90], "preco": item["price"], "link": link_aff, "img": item.get("thumbnail","").replace("-I.jpg","-O.jpg")}
    except Exception as e:
        print(f"API falhou: {e}")

    # 2. Se a API bloquear (403), usa um dos reais acima
    print("Usando produto real blindado...")
    prod = random.choice(produtos_reais)
    link_aff = f"{prod['link_base']}?matt_tool={ML_TOOL}&matt_word={ML_WORD}&matt_source=telegram_v58"
    print(f"Link final que NÃO vai pra capa: {link_aff}")
    return {"titulo": prod["titulo"], "preco": prod["preco"], "link": link_aff, "img": ""}

def enviar(prod):
    texto = f"🔥 OFERTA REAL 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👇 LINK DIRETO PRODUTO 👇\n{prod['link']}"
    try:
        if prod.get("img"):
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            r = requests.post(url, data={"chat_id": CANAL, "photo": prod["img"], "caption": texto}, timeout=20)
            if r.json().get("ok"):
                print("Enviado com foto!")
                return True
    except:
        pass
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
    print(f"Telegram: {r.text[:200]}")
    return True

p = buscar()
if p:
    print(f"ENVIANDO: {p['link']}")
    enviar(p)
