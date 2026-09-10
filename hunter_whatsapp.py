import os, requests, random, time, re
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = "magazineafilliados"

COFRE_OURO = [
    ("TV 43 TCL QLED 43S5K", "240424200"),
    ("iPhone 13 128GB 128GB Meia-noite", "234508500"),
    ("iPhone 14 128GB", "237054500"),
    ("Air Fryer Mondial 4,2L Family", "022255000"),
    ("Air Fryer Philco 4,4L", "234532000"),
    ("Smart TV 50 Crystal 4K Samsung", "237708800"),
    ("Moto G54 5G 128GB", "237707300"),
    ("JBL Boombox 3", "234665100"),
]

def enviar(produto_id, titulo_manual=""):
    link_afiliado = f"https://www.magazinevoce.com.br/{LOJA}/p/{produto_id}/"
    texto = f"""🎉 <b>ANIVERSARIO MAGALU</b>
🔥 <b>{titulo_manual.upper()}</b>

✅ Loja: Afilliados - Influenciador Magalu
✅ Entrega RAPIDA Magalu
✅ Ate 10x sem juros

👇 <b>LINK COM DESCONTO:</b>
{link_afiliado}

#achadosimperdiveis"""

    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML"}, timeout=20)
        print(f"Enviado {titulo_manual} -> {r.status_code}")
        return True
    except Exception as e:
        print(e)
        return False

print(f"=== HUNTER {datetime.now()} ===")
for titulo, pid in random.sample(COFRE_OURO, 3):
    enviar(pid, titulo)
    time.sleep(3)
print("✅ OK")
