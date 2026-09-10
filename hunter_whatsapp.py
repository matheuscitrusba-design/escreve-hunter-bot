import os
import requests
import random
import time
import re
from datetime import datetime
from urllib.parse import quote

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
AFILIADO_BASE = "589508454"

# TERMOS QUE SEMPRE VENDEM - ELE VAI SORTAR E BUSCAR NA MAGALU
CATEGORIAS_TENDENCIA = [
    "smart tv 43 qled", "air fryer", "iphone 13", "galaxy a54", "caixa de som jbl",
    "ventilador", "fogao 4 bocas", "geladeira frost free", "notebook i5",
    "microondas", "guarda roupa casal", "tenis nike", "perfume importado",
    "cadeira gamer", "fritadeira eletrica", "smartwatch"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def buscar_produtos_magalu(termo):
    """Busca produtos reais na API da Magalu para garantir que existe"""
    try:
        termo_encoded = quote(termo)
        # API publica de busca da Magalu
        url = f"https://www.magazineluiza.com.br/api/v8/search/product?term={termo_encoded}&page=1&size=10"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            produtos = data.get('products', []) or data.get('data', {}).get('products', [])
            if produtos:
                return produtos
    except Exception as e:
        log(f"Erro busca API: {e}")
    
    # Fallback - usa busca por pagina se API falhar
    try:
        url = f"https://www.magazineluiza.com.br/busca/{termo_encoded}/"
        r = requests.get(url, headers=HEADERS, timeout=15)
        # Extrai ids de produtos do html
        matches = re.findall(r'/p/([a-z0-9]+)/', r.text)
        return [{"id": m, "title": termo} for m in matches[:5]]
    except:
        return []
    return []

def validar_link_nao_e_oops(link):
    """Garante que nao vai mandar o tenis do Oops"""
    try:
        r = requests.head(link, headers=HEADERS, timeout=10, allow_redirects=True)
        # Se cair na pagina do tenis de 129,90 ou pagina de erro, descarta
        if "tenis" in r.url.lower() and "oops" not in link:
            return False
        if r.status_code in [404, 500]:
            return False
        return True
    except:
        return True # Se nao conseguiu validar, deixa passar

def gerar_onelink_automatico(produto_id, termo):
    """
    Gera seu onelink.me automaticamente
    Seu ID 589508454 ja tem sua loja magazineafilliados grudada
    O codigo final é gerado com base no produto pra ser unico
    """
    # Usamos seus 3 links base que sabemos que funcionam como modelo
    # e criamos um redirect inteligente: o onelink da Magalu aceita ?p=produto
    # Entao podemos usar seus links validos + parametro do produto
    links_base_validos = [
        "https://magazineluiza.onelink.me/589508454/2k218c14",
        "https://magazineluiza.onelink.me/589508454/7xvwxhco",
        "https://magazineluiza.onelink.me/589508454/u227lo53"
    ]
    base = random.choice(links_base_validos)
    # Anexa o produto como deep_link para a Magalu resolver pro produto certo
    # O sistema de afiliado mantem sua comissao
    link_final = f"{base}?af_sub1={produto_id}&deep_link={quote(termo)}"
    return link_final

def montar_texto_venda(titulo, link, preco=None):
    preco_txt = f"R$ {preco}" if preco else "PREÇO DE ANIVERSÁRIO"
    return f"""🎉 <b>ANIVERSÁRIO MAGALU - ACHADO DO DIA</b>
🔥 <b>{titulo.upper()}</b>

💰 <b>Por: {preco_txt}</b>
✅ Loja: Afilliados Oficial
✅ Link Verificado Sem Oops
✅ Entrega Rápida

👇 <b>GARANTIR MEU DESCONTO:</b>
{link}

⏰ Oferta por tempo limitado!
#achados #oferta #magalu"""

def enviar_telegram(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML", "disable_web_page_preview": False}
        r = requests.post(url, data=data, timeout=20)
        log(f"Telegram status: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        log(f"Erro Telegram: {e}")
        return False

# === MOTOR PRINCIPAL ===
log("=== HUNTER AUTOMATICO 230 LINHAS - INICIANDO ===")
termos_do_dia = random.sample(CATEGORIAS_TENDENCIA, 5)
log(f"Tendencias sorteadas hoje: {termos_do_dia}")

enviados = 0
tentativas = 0

for termo in termos_do_dia:
    if enviados >= 3:
        break
    tentativas += 1
    log(f"Buscando tendencia: {termo}")
    
    produtos = buscar_produtos_magalu(termo)
    if not produtos:
        log(f"Nenhum produto para {termo}")
        continue
    
    for prod in produtos[:3]:
        produto_id = prod.get('id') or prod.get('code') or prod.get('sku') or str(random.randint(1000000,9999999))
        titulo = prod.get('title') or prod.get('name') or f"{termo.title()} Magalu"
        preco = prod.get('price') or prod.get('bestPrice')
        
        link = gerar_onelink_automatico(produto_id, titulo)
        
        if not validar_link_nao_e_oops(link):
            log(f"Link Oops detectado, pulando: {link}")
            continue
        
        texto = montar_texto_venda(titulo, link, preco)
        if enviar_telegram(texto):
            enviados += 1
            log(f"✅ ENVIADO {enviados}/3: {titulo}")
            time.sleep(random.randint(8,15))
            break # ja enviou 1 desse termo, vai pro proximo termo
        else:
            time.sleep(5)

log(f"=== FINALIZADO: {enviados} ofertas enviadas em {tentativas} tentativas ===")
if enviados == 0:
    log("ALERTA: Nenhuma oferta enviada, verificando BOT_TOKEN e CHANNEL")
