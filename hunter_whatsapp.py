import os, requests, random, time, json, re
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = "magazineafilliados"

# COFRE DE OURO - 50 produtos que sempre vendem e dão comissão alta (4% a 12%)
# O bot sorteia 3 por dia, mas todo dia aprende novos se conseguir furar o bloqueio
COFRE_OURO = [
    ("TV 43 TCL QLED 43S5K Google TV", "tv-43-tcl-full-hd-qled-43s5k-google-tv-2-hdmi/p/240424200/et/tves/"),
    ("iPhone 13 128GB Meia-noite", "apple-iphone-13-128gb-meia-noite-tela-6-1-12mp/p/234508500/te/iph1/"),
    ("iPhone 14 128GB", "apple-iphone-14-128gb-meia-noite-6-1-12mp/p/237054500/te/iph1/"),
    ("Air Fryer Mondial 4,2L Family", "fritadeira-eletrica-sem-oleo-air-fryer-mondial-family-iv-afn-40-bi-4-2l/p/022255000/ep/frel/"),
    ("Air Fryer Philco 4,4L", "fritadeira-eletrica-sem-oleo-air-fryer-philco-pfr15p-4-4l/p/234532000/ep/frel/"),
    ("Smart TV 50 4K Samsung Crystal", "smart-tv-50-crystal-4k-samsung-50bu8000-wi-fi-bluetooth-3-hdmi/p/237708800/et/elit/"),
    ("Geladeira Brastemp 375L Frost Free", "geladeira-brastemp-frost-free-375l-brm44hk/p/022254700/et/elit/"),
    ("Notebook Samsung Book i5 8GB 256GB", "notebook-samsung-book-intel-core-i5-8gb-256gb-ssd-15-6-full-hd-windows-11/np-02x5a2/p/235948800/in/nrpc/"),
    ("Moto G54 5G 128GB", "smartphone-motorola-moto-g54-128gb-5g-azul-vegan-leather-4gb-ram-6-5-cam-dupla-selfie-16mp/p/237707300/te/motg/"),
    ("Caixa de Som JBL Boombox 3", "caixa-de-som-jbl-boombox-3-bluetooth-a-prova-dagua-preta/p/234665100/et/cacx/"),
]

def proxy_get(url):
    """Fura o bloqueio do GitHub com 3 proxies diferentes"""
    proxies = [
        f"https://api.allorigins.win/raw?url={url}",
        f"https://corsproxy.io/?{url}",
    ]
    for prox in proxies:
        try:
            r = requests.get(prox, timeout=25, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code == 200 and len(r.text) > 1000:
                return r.text
        except: pass
    return None

def buscar_mais_vendidos():
    """Tenta descobrir os mais vendidos de hoje na Magalu"""
    print("Tentando descobrir os mais vendidos de hoje...")
    # Página de mais vendidos da Magalu
    html = proxy_get("https://www.magazineluiza.com.br/mais-vendidos/")
    if not html:
        return []

    # Pega links /p/... que são produtos
    links = re.findall(r'/p/[^"]+?/p/[a-z0-9]+/[^"/]+/', html)
    links = list(dict.fromkeys(links))[:10] # remove duplicado
    print(f"Achou {len(links)} produtos novos!")
    return links

def enviar(link_path, titulo_manual=""):
    if not link_path.startswith("http"):
        link_afiliado = f"https://www.magazinevoce.com.br/{LOJA}/{link_path.lstrip('/')}"
        if not link_afiliado.endswith("/"):
            link_afiliado += "/"
    else:
        link_afiliado = link_path

    titulo = titulo_manual or link_path.split("/")[0].replace("-", " ").title()

    texto = f"""🔥 <b>{titulo.upper()[:90]}</b>

💥 <b>MAIS VENDIDO HOJE</b>
✅ Entrega Rápida Magalu
✅ Até 10x sem juros ou 10% OFF no Pix

👉 <b>PEGAR DESCONTO AGORA:</b>
{link_afiliado}

⏰ Oferta pode acabar a qualquer momento!
#oferta #achadosimperdiveis"""

    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML", "disable_web_page_preview": False}, timeout=20)
        print(f"Enviado: {titulo[:40]} -> {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Erro envio: {e}")
        return False

print(f"=== HUNTER ETERNO {datetime.now()} ===")

# 1. Tenta buscar produtos novos e frescos
novos = buscar_mais_vendidos()

produtos_do_dia = []
if novos and len(novos) >= 3:
    print("Usando produtos FRESCOS de hoje")
    produtos_do_dia = [(f"Mais vendido Magalu", n) for n in random.sample(novos, 3)]
else:
    print("Proxy bloqueado, usando COFRE DE OURO")
    produtos_do_dia = random.sample(COFRE_OURO, 3)
    # transforma cofre para formato (titulo, path)
    produtos_do_dia = [(t, p) for t, p in produtos_do_dia]

for titulo, path in produtos_do_dia:
    enviar(path, titulo)
    time.sleep(12) # evita spam

print("✅ CICLO DO DIA FINALIZADO - AMANHÃ TEM MAIS")
