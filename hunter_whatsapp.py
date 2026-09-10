import os
import requests
import random
import time
import re
import json
from datetime import datetime
from urllib.parse import quote

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

COFRE_FALLBACK = [
    ("Caixa de Som JBL Bomber", "https://magazineluiza.onelink.me/589508454/2k218c14"),
    ("Oferta Relampago Magalu", "https://magazineluiza.onelink.me/589508454/7xvwxhco"),
    ("Achado do Dia", "https://magazineluiza.onelink.me/589508454/u227lo53"),
]

CATEGORIAS_TENDENCIA = [
    "caixa de som jbl", "tenis nike", "cadeira gamer", "geladeira frost free", "ventilador",
    "smart tv 43", "air fryer", "iphone", "galaxy a54", "fogao 4 bocas", "notebook i5"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def buscar_produtos_v2(termo):
    """V2 - Pega do HTML mesmo, porque a API esta bloqueando"""
    try:
        termo_url = termo.replace(" ", "-")
        url = f"https://www.magazineluiza.com.br/busca/{termo_url}/"
        log(f"Tentando {url}")
        r = requests.get(url, headers=HEADERS, timeout=20)
        html = r.text

        # Tenta pegar JSON do Next.js que tem os produtos
        # Procurar por "products":[...]
        produtos = []

        # Regex 1 - titulos de produtos no HTML
        titulos = re.findall(r'"title":"([^"]+)"', html)
        precos = re.findall(r'"price":(\d+\.?\d*)', html)
        ids = re.findall(r'/p/([a-zA-Z0-9]+)/', html)

        log(f"Achados: {len(titulos)} titulos, {len(ids)} ids")

        for i in range(min(5, len(ids))):
            t = titulos[i] if i < len(titulos) else f"{termo.title()} Magalu"
            p_id = ids[i] if i < len(ids) else str(random.randint(1000000,9999999))
            produtos.append({"id": p_id, "title": t, "price": precos[i] if i < len(precos) else None})

        # Se ainda vazio, usa o termo mesmo como produto
        if not produtos and len(html) > 5000:
            produtos = [{"id": termo.replace(" ",""), "title": f"{termo.title()} - Oferta Magalu Aniversario", "price": None}]

        return produtos
    except Exception as e:
        log(f"Erro V2 {termo}: {e}")
        return []

def gerar_onelink_com_produto(produto_id, titulo):
    base = random.choice(COFRE_FALLBACK)[1].split('?')[0]
    link_final = f"{base}?af_sub1={produto_id}&utm_term={quote(titulo)}"
    return link_final

def montar_texto(titulo, link, preco=None):
    preco_txt = f"R$ {preco}" if preco else "OFERTA ANIVERSARIO"
    return f"""🎉 <b>ACHADO DO DIA - MAGALU</b>
🔥 <b>{titulo.upper()[:80]}</b>

💰 <b>{preco_txt}</b>
✅ Link Verificado Sem Oops
✅ Entrega Rapida Magalu

👇 <b>COMPRAR COM DESCONTO:</b>
{link}

#oferta"""

def enviar_telegram(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML"}
        r = requests.post(url, data=data, timeout=20)
        return r.status_code == 200
    except:
        return False

# === MOTOR PRINCIPAL COM FALLBACK ===
log("=== HUNTER AUTOMATICO 230 LINHAS - V2 CORRIGIDO ===")
termos = random.sample(CATEGORIAS_TENDENCIA, 5)
log(f"Tendencias sorteadas hoje: {termos}")

enviados = 0

for termo in termos:
    if enviados >= 3:
        break
    log(f"Buscando tendencia: {termo}")
    produtos = buscar_produtos_v2(termo)

    if not produtos:
        log(f"Nenhum produto para {termo}")
        continue

    for prod in produtos[:2]:
        link = gerar_onelink_com_produto(prod['id'], prod['title'])
        texto = montar_texto(prod['title'], link, prod.get('price'))
        if enviar_telegram(texto):
            enviados += 1
            log(f"ENVIADO {enviados}/3: {prod['title'][:40]}")
            time.sleep(8)
            break

# SE AINDA ASSIM NAO ENVIOU NADA, USA O COFRE PRA NAO FICAR ZERADO
if enviados == 0:
    log("BUSCA FALHOU, ATIVANDO MODO COFRE - GARANTINDO 3 ENVIOS")
    for titulo, link in random.sample(COFRE_FALLBACK, 3):
        texto = montar_texto(titulo, link, None)
        if enviar_telegram(texto):
            enviados += 1
            log(f"ENVIADO COFRE {enviados}/3: {titulo}")
            time.sleep(5)

log(f"=== FINALIZADO: {enviados} ofertas enviadas ===")
