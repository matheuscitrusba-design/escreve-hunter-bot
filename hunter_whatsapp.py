import os, requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")

# LINK REAL E VIVO TESTADO AGORA - ABRE DIRETO NO PRODUTO
LINK_VIVO = "https://produto.mercadolivre.com.br/MLB-5403571651-echo-dot-5-geracao-alexa-amazon-completo-_JM?matt_tool=77761463&matt_word=matheus20190&forceInApp=true"

def enviar():
    texto = f"""🔥 TESTE DE LINK VIVO 🔥

📦 Echo Dot 5ª Geração Alexa Original

💰 R$ 299

👇 CLICA AQUI - TEM QUE ABRIR NO PRODUTO DIRETO 👇
{LINK_VIVO}

Se abrir no produto, seu afiliado está 100% certo."""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
    print(r.text)

enviar()
