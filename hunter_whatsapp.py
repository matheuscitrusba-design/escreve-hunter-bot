import os, requests, random, time

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190g"

def link_valido(url):
    try:
        # Testa se a página existe mesmo
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        return r.status_code < 400
    except:
        return True # se não conseguir testar, deixa passar

def buscar():
    print("Hunter V5.3 - Blindado contra link quebrado...")
    termos = ["iphone 13 128gb", "jbl boombox", "air fryer mondia", "xiaomi smartwatch", "ps5 slim", "tenis nike air", "notebook samsung", "echo dot 5 alexa"]
    random.shuffle(termos)

    headers = {"User-Agent": "Mozilla/5.0"}

    for termo in termos:
        print(f"Buscando: {termo}")
        try:
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=20&sort=sold_quantity_desc"
            data = requests.get(url, headers=headers, timeout=20).json()

            for p in data.get("results", []):
                link_base = p.get("permalink","")
                if not link_base or "MLB" not in link_base:
                    continue

                # LIMPA o link - tira? e # pra não quebrar
                link_base = link_base.split("?")[0].split("#")[0].strip()

                # Verifica se o link base existe
                if not link_valido(link_base):
                    print(f"Link quebrado pulado: {link_base}")
                    continue

                # Gera afiliado CORRETO - usa & se precisar
                link_aff = f"{link_base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}&matt_source=telegram_v53"

                print(f"LINK OK: {p['title'][:50]} -> {link_aff}")
                return {
                    "titulo": p["title"][:90],
                    "preco": p["price"],
                    "link": link_aff,
                    "img": p.get("thumbnail","").replace("-I.jpg","-O.jpg"),
                    "termo": termo
                }
        except Exception as e:
            print(f"Erro busca {termo}: {e}")
            continue
    return None

def enviar(prod):
    texto = f"🔥 ACHADO TESTADO 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👇 LINK QUE FUNCIONA 👇\n{prod['link']}"
    try:
        # Tenta com foto
        if prod["img"]:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            r = requests.post(url, data={"chat_id": CANAL, "photo": prod["img"], "caption": texto}, timeout=20)
            if r.json().get("ok"):
                print(f"Enviado com foto: {r.text[:150]}")
                return True

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
        print(f"Telegram: {r.text[:150]}")
        return r.json().get("ok", False)
    except Exception as e:
        print(f"Erro envio: {e}")
        return False

prod = buscar()
if prod:
    enviar(prod)
else:
    print("Nada válido achado")
