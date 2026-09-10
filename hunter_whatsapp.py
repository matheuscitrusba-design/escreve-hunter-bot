import os, sys, requests, smtplib
from email.mime.text import MIMEText
from datetime import datetime

ARQ_SALDO = "saldo.txt"
CUSTO_DIA = 0.20
SEU_LINK = "https://meli.la/1xJ45o4"

if not os.path.exists(ARQ_SALDO):
    with open(ARQ_SALDO, "w") as f: f.write("10.0")
with open(ARQ_SALDO, "r") as f: saldo = float(f.read())
if saldo <= 0: sys.exit()

novo_saldo = saldo - CUSTO_DIA
with open(ARQ_SALDO, "w") as f: f.write(str(novo_saldo))

termo = "suporte celular led"
produtos = requests.get(f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=2").json().get('results', [])

corpo = f"""
Hunter - {datetime.now().strftime('%d/%m/%Y %H:%M')} Inhambupe
Saldo: ${novo_saldo:.2f} | Dias: {novo_saldo/0.20:.0f}
Seu Link Filial ML: {SEU_LINK}

Produto hoje: {termo}
Link pra postar: {SEU_LINK}

Vendeu 1 = +$0,72 no saldo, nao morre mais.
Bateu $20 = se duplica em 2.
"""

msg = MIMEText(corpo)
msg['Subject'] = f"Hunter ML HOJE - Saldo ${novo_saldo:.2f} - {termo}"
msg['From'] = os.getenv("EMAIL_ORIGEM")
msg['To'] = os.getenv("EMAIL_DESTINO")

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(os.getenv("EMAIL_ORIGEM"), os.getenv("EMAIL_SENHA_APP"))
    server.send_message(msg)

print(f"Email enviado pra {os.getenv('EMAIL_DESTINO')} Saldo {novo_saldo}")
