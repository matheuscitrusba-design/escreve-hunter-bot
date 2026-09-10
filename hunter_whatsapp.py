import os
import requests
import random
import time
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

# SEUS 3 LINKS VALIDADOS - SEM OOPS
COFRE_OURO = [
    ("TV 43 TCL QLED 43S5K", "https://magazineluiza.onelink.me/589508454/2k218c14"),
    ("Oferta Magalu 2", "https://magazineluiza.onelink.me/589508454/7xvwxhco"),
    ("Oferta Magalu 3", "https://magazineluiza.onelink.me/589508454/u227lo53"),
]

def enviar(link, titulo):
    texto = f"""🎉 <b>ANIVERSARIO MAGALU - LOJA AFILLIADOS</b>
🔥 <b>{titulo.upper()}</b>

✅ Loja Oficial Afilliados
✅ Entrega Rapida Magalu
✅ Ate 10x sem juros

👇 <b>PEGAR DESCONTO AGORA:</b>
{link}

⏰ Estoque acabando rapido!
#oferta #achados"""

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHANNEL,
            "text": texto,
            "parse_mode": "HTML"
        }
        r = requests.post(url, data=data, timeout=20)
        print(f"[{datetime.now()}] Enviado: {titulo} -> Status {r.status_code}")
        return True
    except Exception as e:
        print(f"Erro ao enviar {titulo}: {e}")
        return False

print(f"=== HUNTER WHATSAPP - ONELINK - {datetime.now()} ===")
print(f"Total de ofertas: {len(COFRE_OURO)}")

# Envia em ordem aleatoria
for titulo, link in random.sample(COFRE_OURO, len(COFRE_OURO)):
    enviar(link, titulo)
    time.sleep(5)

print("✅ CICLO FINALIZADO - 0% CHANCE DE OOPS")
