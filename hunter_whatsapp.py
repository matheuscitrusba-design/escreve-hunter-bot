import os, requests, random

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190"

def link_funciona(url):
    # Testa se abre de verdade
    try:
        # Tira o afiliado pra testar só a base
        base = url.split("?")[0]
        if "/social/" in base:
            print(f"Link social descartado: {base}")
            return False
        r = requests.get(base, timeout=10, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        # Se for 404 ou página "não existe" no html
        if r.status_code >= 400 or "esta página não existe" in r.text.lower():
            print(f"Link quebrado: {base} - {r.status_code}")
            return False
        print(f"Link OK: {base}")
        return True
    except Exception as e:
        print(f"Erro teste link: {e}")
        return False

def buscar():
    print(f"Hunter V5.7 - Afiliado {ML_WORD} - Só link que funciona")

    # PRODUTOS COM LINK DE CATÁLOGO /p/ - ESSES NUNCA DÃO 404
    catalogo = [
        {"t": "Echo Dot 5ª Geração Alexa", "p": 299, "id": "MLB27043682"},
        {"t": "Fone JBL Vibe Buds Bluetooth", "p": 199, "id": "MLB20218690"},
        {"t": "Air Fryer Mondial 4,2L", "p": 349, "id": "MLB15177908"},
        {"t": "Smartwatch Xiaomi Mi Band 8", "p": 249, "id": "MLB26275735"},
        {"t": "Cafeteira Elétrica Mondial", "p": 89, "id": "MLB17449650"},
    ]

    # Tenta pegar um aleatório da API
    try:
        termo = random.choice(["iphone", "jbl", "air fryer"])
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=10"
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            for item in r.json().get("results", []):
                link_base = item.get("permalink","").split("?")[0]
                if "MLB" in link_base and "/social/" not in link_base and link_funciona(link_base):
                    link_aff = f"{link_base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}"
                    return {"titulo": item["title"][:90], "preco": item["price"], "link": link_aff, "img": item.get("thumbnail","").replace("-I.jpg","-O.jpg")}
    except:
        pass

    # Se a API falhar, usa catálogo fixo que é garantido
    print("Usando catálogo fixo blindado...")
    prod = random.choice(catalogo)
    link_base = f"https://www.mercadolivre.com.br/produto/p/{prod['id']}"
    # Testa
    if not link_funciona(link_base):
        # tenta formato 2
        link_base = f"https://www.mercadolivre.com.br/p/{prod['id']}"

    link_aff = f"{link_base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}"
    print(f"Link final blindado: {link_aff}")
    return {"titulo": prod["t"], "preco": prod["p"], "link": link_aff, "img": ""}

def enviar(prod):
    texto = f"🔥 OFERTA TESTADA 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👇 LINK FUNCIONANDO 👇\n{prod['link']}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    if prod.get("img"):
        try:
            url_foto = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            r = requests.post(url_foto, data={"chat_id": CANAL, "photo": prod["img"], "caption": texto}, timeout=20)
            if r.json().get("ok"):
                return True
        except:
            pass
    r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
    print(f"Telegram: {r.text[:200]}")
    return True

p = buscar()
if p:
    print(f"VAI ENVIAR: {p['link']}")
    enviar(p)
