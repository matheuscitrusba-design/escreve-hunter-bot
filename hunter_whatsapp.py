import os, requests, smtplib, random
from email.mime.text import MIMEText
from datetime import datetime

# SEUS DADOS
MATT_TOOL = "77761463"
MATT_WORD = "matheus20190"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL", "@achadosmercadolivrebrasil")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

def caçar_produto():
    termos = ["creatina 1kg", "whey protein", "fone bluetooth", "smartwatch", "air fryer"]
    termo = random.choice(termos)
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=5"
    r = requests.get(url).json()
    for item in r.get("results", []):
        if item.get("id"):
            link_afiliado = f"https://www.mercadolivre.com.br/{item['id']}?matt_tool={MATT_TOOL}&matt_word={MATT_WORD}"
            return {
                "titulo": item["title"],
                "preco": item["price"],
                "link": link_afiliado,
                "img": item["thumbnail"]
            }
    return None

def postar_telegram(produto):
    if not TELEGRAM_BOT_TOKEN: return
    texto = f"🔥 OFERTA ACHADA PELA IA\n\n{produto['titulo']}\n💰 Por R$ {produto['preco']}\n\n👉 Compre aqui: {produto['link']}\n\n#achados #oferta #mercadolivre"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHANNEL, "text": texto})
    print("Postado no Telegram!")

def enviar_email(produto):
    msg = MIMEText(f"Oferta: {produto['titulo']} - {produto['link']}")
    msg["Subject"] = f"IA Vendeu: {produto['titulo']}"
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_USER, GMAIL_PASS)
            s.send_message(msg)
    except: pass

# RODA
produto = caçar_produto()
if produto:
    postar_telegram(produto)
    enviar_email(produto)
    print(f"V5 OK - {produto['titulo']}")
