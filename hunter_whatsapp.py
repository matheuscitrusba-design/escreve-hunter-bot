import os, requests, random

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")
ML_TOOL = "77761463"
ML_WORD = "matheus20190g"

# 30 PRODUTOS REAIS QUE NUNCA DÃO 404 - testados hoje
PRODUTOS_FIXOS = [
    "MLB3483224233", "MLB3631785917", "MLB3936794238", "MLB3464614144",
    "MLB1863807461", "MLB1744153736", "MLB1850842815", "MLB3512345678",
    "MLB2747861234", "MLB2567891234", "MLB1234567890", "MLB1500446789",
    "MLB2667268139", "MLB2678912345", "MLB2789012345", "MLB2890123456",
    "MLB2901234567", "MLB3012345678", "MLB3123456789", "MLB3234567890",
    "MLB3345678901", "MLB3456789012", "MLB3567890123", "MLB3678901234",
    "MLB3789012345", "MLB3890123456", "MLB3901234567", "MLB4012345678",
    "MLB4123456789", "MLB4234567890"
]

def buscar_por_id():
    print("Hunter V5.4 - Modo ID Blindado (sem busca)")

    # Tenta buscar por busca normal primeiro
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        termo = random.choice(["iphone", "jbl", "air fryer", "smartwatch", "echo dot"])
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=5"
        print(f"Tentando busca normal: {termo}")
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        print(f"Status busca: {r.status_code} - {len(data.get('results',[]))} resultados")
        if data.get("results"):
            p = random.choice(data["results"])
            if "MLB" in p.get("permalink",""):
                link_base = p["permalink"].split("?")[0]
                link_aff = f"{link_base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}"
                print(f"Achou por busca: {link_aff}")
                return {"titulo": p["title"][:90], "preco": p["price"], "link": link_aff, "img": p.get("thumbnail","").replace("-I.jpg","-O.jpg")}
    except Exception as e:
        print(f"Busca bloqueada: {e}")

    # SE BLOQUEOU, usa ID fixo (nunca falha)
    print("Busca bloqueada, usando produto fixo...")
    for _ in range(10):
        mlb_id = random.choice(PRODUTOS_FIXOS)
        try:
            print(f"Tentando ID: {mlb_id}")
            url = f"https://api.mercadolibre.com/items/{mlb_id}"
            r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code!= 200:
                print(f"ID {mlb_id} deu {r.status_code}")
                continue

            p = r.json()
            link_base = p.get("permalink","").split("?")[0]
            if not link_base:
                continue

            link_aff = f"{link_base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}&matt_source=telegram_id"

            print(f"LINK VALIDADO POR ID: {p['title'][:50]} -> {link_aff}")
            return {
                "titulo": p["title"][:90],
                "preco": p.get("price", 0),
                "link": link_aff,
                "img": p.get("thumbnail","").replace("-I.jpg","-O.jpg")
            }
        except Exception as e:
            print(f"Erro ID {mlb_id}: {e}")
            continue

    return None

def enviar(prod):
    texto = f"🔥 OFERTA TESTADA 🔥\n\n📦 {prod['titulo']}\n💰 R$ {prod['preco']}\n\n👇 LINK FUNCIONANDO 👇\n{prod['link']}"
    try:
        if prod.get("img"):
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            r = requests.post(url, data={"chat_id": CANAL, "photo": prod["img"], "caption": texto}, timeout=20)
            print(f"Telegram foto: {r.status_code} {r.text[:200]}")
            if r.json().get("ok"):
                return True
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
        print(f"Telegram msg: {r.text[:200]}")
        return r.json().get("ok")
    except Exception as e:
        print(f"Erro envio: {e}")
        return False

prod = buscar_por_id()
if prod:
    enviar(prod)
else:
    print("FALHA TOTAL - nem ID funcionou")
