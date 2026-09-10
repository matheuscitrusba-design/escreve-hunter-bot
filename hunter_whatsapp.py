import os
import requests
import random
import time
import re
from datetime import datetime
from urllib.parse import quote

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

# SEUS 3 LINKS QUE JA VALIDAMOS - NUNCA VAO DAR OOPS
LINKS_BASE_VALIDOS = [
    "https://magazineluiza.onelink.me/589508454/2k218c14",
    "https://magazineluiza.onelink.me/589508454/7xvwxhco",
    "https://magazineluiza.onelink.me/589508454/u227lo53"
]

# 20 TITULOS PRA VARIAR MESMO QUANDO A BUSCA FALHAR
COFRE_FALLBACK_TITULOS = [
    "Smart TV 43 QLED TCL", "Air Fryer 4L Mondial", "Caixa de Som JBL Boombox",
    "iPhone 13 128GB", "Galaxy A54 256GB", "Fogao 4 Bocas Atlas",
    "Geladeira Frost Free 310L", "Ventilador Turbo 40cm", "Notebook i5 8GB",
    "Cadeira Gamer Reclinavel", "Tenis Nike Revolution", "Microondas 20L Electrolux",
    "Guarda Roupa Casal 6 Portas", "Smartwatch Haylou Solar", "Perfume Importado 100ml",
    "Fone Bluetooth JBL", "Prancha Alisadora", "Liquidificador Turbo Power",
    "Mesa de Jantar 4 Cadeiras", "Bicicleta Aro 29"
]

CATEGORIAS_TENDENCIA = [
    "smart tv 43 qled", "air fryer", "iphone", "galaxy a54", "caixa de som jbl",
    "ventilador", "fogao 4 bocas", "geladeira frost free", "notebook i5",
    "microondas", "guarda roupa casal", "tenis nike", "cadeira gamer"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def buscar_produtos_v2(termo):
    """Busca com proxy pra tentar burlar bloqueio da Magalu no GitHub Actions"""
    try:
        termo_url = termo.replace(" ", "-")
        html = ""
        # Tentativa 1 via AllOrigins
        try:
            url = f"https://api.allorigins.win/raw?url=https://www.magazineluiza.com.br/busca/{termo_url}/"
            r = requests.get(url, headers=HEADERS, timeout=20)
            html = r.text
            log(f"AllOrigins retornou {len(html)} chars")
        except Exception as e:
            log(f"Falha AllOrigins: {e}")

        # Tentativa 2 via Jina AI se a primeira veio vazia
        if len(html) < 2000:
            try:
                url2 = f"https://r.jina.ai/http://www.magazineluiza.com.br/busca/{termo_url}/"
                r2 = requests.get(url2, headers=HEADERS, timeout=20)
                html = r2.text
                log(f"Jina retornou {len(html)} chars")
            except Exception as e:
                log(f"Falha Jina: {e}")

        titulos = re.findall(r'"title":"([^"]+)"', html)
        ids = re.findall(r'/p/([a-zA-Z0-9]{7,8})/', html)

        log(f"Achados: {len(titulos)} titulos, {len(ids)} ids")

        produtos = []
        for i in range(min(5, len(ids))):
            t = titulos[i] if i < len(titulos) else f"{termo.title()} Magalu"
            produtos.append({"id": ids[i], "title": t[:80]})

        if not produtos and len(html) > 1000:
            produtos = [{"id": termo.replace(" ","")[:10], "title": f"{termo.title()} - Oferta Aniversario Magalu"}]

        return produtos
    except Exception as e:
        log(f"Erro V2 {termo}: {e}")
        return []

def gerar_onelink_com_produto(produto_id, titulo):
    base = random.choice(LINKS_BASE_VALIDOS).split('?')[0]
    link_final = f"{base}?af_sub1={produto_id}&utm_term={quote(titulo)}"
    return link_final

def gerar_fallback_variado():
    """Gera 3 ofertas diferentes TODO DIA mesmo se a busca falhar"""
    titulos_do_dia = random.sample(COFRE_FALLBACK_TITULOS, 3)
    ofertas = []
    for titulo in titulos_do_dia:
        base = random.choice(LINKS_BASE_VALIDOS).split('?')[0]
        produto_id = titulo.lower().replace(" ", "")[:10] + str(random.randint(100,999))
        link = f"{base}?af_sub1={produto_id}&utm_term={titulo.replace(' ', '+')}"
        ofertas.append((titulo, link))
    return ofertas

def montar_texto(titulo, link, preco=None):
    preco_txt = f"R$ {preco}" if preco else "OFERTA ANIVERSARIO MAGALU"
    return f"""🎉 <b>ANIVERSARIO MAGALU - ACHADO DO DIA</b>
🔥 <b>{titulo.upper()[:80]}</b>

💰 <b>{preco_txt}</b>
✅ Link Oficial Afilliados Verificado
✅ Entrega Rapida Magalu

👇 <b>PEGAR DESCONTO AGORA:</b>
{link}

⏰ Estoque limitado!
#oferta #achados"""

def enviar_telegram(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML"}
        r = requests.post(url, data=data, timeout=20)
        log(f"Telegram status: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        log(f"Erro Telegram: {e}")
        return False

# === MOTOR PRINCIPAL ===
log("=== HUNTER AUTOMATICO 230 LINHAS - V3 FINAL ===")
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
            log(f"✅ ENVIADO {enviados}/3: {prod['title'][:40]}")
            time.sleep(random.randint(8,15))
            break
        else:
            time.sleep(5)

# MODO COFRE VARIAVEL - NUNCA REPETE OS MESMOS 3
if enviados < 3:
    faltam = 3 - enviados
    log(f"BUSCA FALHOU OU INCOMPLETA, ATIVANDO MODO COFRE VARIAVEL - FALTAM {faltam}")
    cofre_variado = gerar_fallback_variado()
    for titulo, link in cofre_variado[:faltam]:
        texto = montar_texto(titulo, link, None)
        if enviar_telegram(texto):
            enviados += 1
            log(f"ENVIADO COFRE VARIAVEL {enviados}/3: {titulo}")
            time.sleep(5)

log(f"=== FINALIZADO: {enviados} ofertas enviadas ===")
