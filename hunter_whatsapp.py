import os
import requests
import random
from datetime import datetime

# CONFIG
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL", "@achadosmercadolivrebrasil")
ML_AFFILIATE = "matheus20190g" # seu ID
ML_TOOL = "77761463"

def buscar_tendencia():
    """Busca produtos em alta - com proteção contra lista vazia"""
    try:
        print("Hunter V5 - Caçando tendência e gerando afiliado automático...")
        # Busca aleatória no ML para variar
        termos = ["creatina", "whey", "fone bluetooth", "smartwatch", "air fryer", "cadeira gamer"]
        termo = random.choice(termos)
        
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=10"
        r = requests.get(url, timeout=10).json()
        
        results = r.get("results", [])
        if not results:
            print(f"Erro busca: Nenhum resultado para {termo}")
            return None
            
        # Pega um aleatório pra não repetir
        prod = random.choice(results)
        titulo = prod.get("title", "Produto ML")[:100]
        link_original = prod.get("permalink", "")
        preco = prod.get("price", 0)
        
        # Gera link afiliado
        link_afiliado = f"{link_original}?matt_tool={ML_TOOL}&matt_word={ML_AFFILIATE}&matt_source=HunterV5"
        
        return {"titulo": titulo, "preco": preco, "link": link_afiliado, "termo": termo}
        
    except Exception as e:
        print(f"Erro busca: {e}")
        return None

def enviar_telegram(prod):
    if not TOKEN:
        print("ERRO: TELEGRAM_BOT_TOKEN não configurado no Render!")
        return False
    if not CANAL:
        print("ERRO: TELEGRAM_CHANNEL não configurado!")
        return False

    texto = f"""🔥 ACHADO IMPERDÍVEL 🔥

📦 {prod['titulo']}
💰 Por: R$ {prod['preco']}

👉 Link com DESCONTO:
{prod['link']}

⚡️ Visto em: {prod['termo']}
#achados #mercadolivre #promo"""

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CANAL, "text": texto, "disable_web_page_preview": False}
        resp = requests.post(url, data=payload, timeout=15)
        print(f"Telegram response: {resp.text}")
        if resp.status_code == 200:
            print(f"V5 enviado! Produto: {prod['titulo']} | Link: {prod['link']}")
            return True
        else:
            print(f"Falha Telegram: {resp.text}")
            return False
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")
        return False

if __name__ == "__main__":
    prod = buscar_tendencia()
    if prod:
        enviar_telegram(prod)
    else:
        print("Nenhum produto encontrado dessa vez.")
