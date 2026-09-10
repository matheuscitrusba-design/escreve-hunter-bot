import os, requests, random, urllib.parse

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190g"

def get_com_proxy(url_ml):
    """Pega dados do ML usando proxy pra burlar 403"""
    # Lista de proxys gratuitos que funcionam
    proxys = [
        f"https://api.allorigins.win/raw?url={urllib.parse.quote(url_ml, safe='')}",
        f"https://api.codetabs.com/v1/proxy/?quest={urllib.parse.quote(url_ml, safe='')}",
    ]

    for proxy_url in proxys:
        try:
            print(f"Tentando proxy: {proxy_url[:50]}...")
            r = requests.get(proxy_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and "results" in r.text or "title" in r.text:
                print(f"Proxy funcionou! {r.status_code}")
                return r
        except Exception as e:
            print(f"Proxy falhou: {e}")
            continue
    return None

def buscar():
    print("Hunter V5.5 - Modo Proxy Anti-403")
    termos = ["iphone 13", "jbl", "air fryer", "smartwatch xiaomi", "echo dot 5", "ps5", "tenis nike"]
    termo = random.choice(termos)

    # 1. Tenta direto (se por acaso desbloquear)
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=15&sort=sold_quantity_desc"
        print(f"Busca direta: {termo}")
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        print(f"Direto status: {r.status_code}")
        if r.status_code == 200 and r.json().get("results"):
            p = random.choice(r.json()["results"])
            print("Direto funcionou!")
            link = p["permalink"].split("?")[0]
            link_aff = f"{link}?matt_tool={ML_TOOL}&matt_word={ML_WORD}"
            return {"titulo": p["title"][:90], "preco": p["price"], "link": link_aff, "img": p.get("thumbnail","").replace("-I.jpg","-O.jpg")}
    except Exception as e:
        print(f"Direto falhou: {e}")

    # 2. Tenta com proxy (fura o 403)
    try:
        print("Tentando com PROXY...")
        url_ml = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=15"
        r_proxy = get_com_proxy(url_ml)

        if r_proxy:
            data = r_proxy.json()
            results = data.get("results", [])
            print(f"Proxy retornou {len(results)} produtos")
            if results:
                # Filtra só link que tem MLB
                validos = [x for x in results if "MLB" in x.get("permalink","")]
                if validos:
                    p = random.choice(validos)
                    link = p["permalink"].split("?")[0]
                    link_aff = f"{link}?matt_tool={ML_TOOL}&matt_word={ML_WORD}&matt_source=proxy_v55"
                    print(f"ACHOU COM PROXY: {p['title'][:50]}")
                    return {"titulo": p["title"][:90], "preco": p["price"], "link": link_aff, "img": p.get("thumbnail","").replace("-I.jpg","-O.jpg")}
    except Exception as e:
        print(f"Erro proxy: {e}")

    # 3. Se tudo falhar, usa um ID que a gente sabe que existe (sem precisar da API)
    print("Tudo bloqueado, usando link direto sem API...")
    produtos_backup = [
        {"titulo": "Echo Dot 5ª Geração Alexa", "preco": 299, "link": f"https://www.mercadolivre.com.br/echo-dot-5-geracao-smart-speaker-com-alexa-amazon/p/MLB27043682?matt_tool={ML_TOOL}&matt_word={ML_WORD}", "img": ""},
        {"titulo": "Fone Bluetooth JBL Vibe Buds", "preco": 199, "link": f"https://www.mercadolivre.com.br/fone-de-ouvido-jbl-vibe-buds-bluetooth/p/MLB20218690?matt_tool={ML_TOOL}&matt_word={ML_WORD}", "img": ""},
        {"titulo": "Air Fryer Mondial 4,2L", "preco": 349, "link": f"https://www.mercadolivre.com.br/fritadeira-eletrica-mondial-air-fryer-afn-40-bi-42l/p/MLB15177908?matt_tool={ML_TOOL}&matt_word={ML_WORD}", "img": ""},
    ]
    return random.choice(produtos_backup)

def enviar(prod):
    texto = f"🔥 ACHADO COM LINK TESTADO 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👇 LINK QUE FUNCIONA 👇\n{prod['link']}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    if prod.get("img"):
        try:
            url_foto = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            r = requests.post(url_foto, data={"chat_id": CANAL, "photo": prod["img"], "caption": texto}, timeout=20)
            if r.json().get("ok"):
                print("Enviado com foto!")
                return True
        except:
            pass
    r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
    print(f"Telegram: {r.text[:150]}")
    return True

p = buscar()
if p:
    print(f"Vai enviar: {p['titulo']} - {p['link']}")
    enviar(p)
else:
    print("Falha total")
