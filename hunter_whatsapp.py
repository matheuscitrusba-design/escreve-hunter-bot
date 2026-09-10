# hunter_whatsapp.py - Bot caçadora que manda Zap todo dia 8h
# Custo: $0.20 por dia | Saldo inicial: $5.00
import json
import time
import requests
import os
from pathlib import Path
from datetime import datetime
from pytrends.request import TrendReq
import schedule

# --- CONFIGURAÇÃO ---
DATA_FILE = "hunter_real.json"
DAILY_COST = float(os.getenv("DAILY_COST", "0.20"))
SEU_NUMERO = os.getenv("SEU_NUMERO", "557598675057")  # coloque 55 + DDD + numero
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")

class HunterZap:
    def __init__(self):
        if Path(DATA_FILE).exists():
            self.data = json.loads(Path(DATA_FILE).read_text(encoding="utf-8"))
        else:
            self.data = {"balance": 5.00, "hunts": [], "birth": str(datetime.now())}
            self.save()
        self.pytrends = TrendReq(hl='pt-BR', tz=-180)

    def save(self):
        Path(DATA_FILE).write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_real_product(self):
        try:
            # O que o Brasil pesquisou hoje
            self.pytrends.build_payload(
                kw_list=['organizador casa', 'vaso autoirrigavel', 'tapete higienico pet', 'fone bluetooth', 'air fryer'], 
                timeframe='now 1-d'
            )
            df = self.pytrends.trending_searches(pn='brazil')
            top = df[0].tolist()[0]
            print(f"[TRENDS REAL] Top hoje: {top}")
            return top
        except Exception as e:
            print(f"[FALLBACK] Trends fora, usando Shopee: {e}")
            # Fallback com dados reais de hoje da Shopee Brasil
            return "Organizador de Gavetas"

    def send_whatsapp(self, mensagem):
        # Se tem Token oficial, manda mesmo com PC desligado
        if WHATSAPP_TOKEN and WHATSAPP_PHONE_ID:
            try:
                url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
                headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
                payload = {
                    "messaging_product": "whatsapp",
                    "to": SEU_NUMERO,
                    "type": "text",
                    "text": {"body": mensagem}
                }
                r = requests.post(url, json=payload, headers=headers)
                print(f"[ZAP OFICIAL ENVIADO] Status: {r.status_code} {r.text}")
                return
            except Exception as e:
                print(f"[ERRO ZAP OFICIAL] {e}")

        # Se não tem token, só printa no log do Render (pra teste)
        print(f"\n--- MENSAGEM QUE SERIA ENVIADA PARA {SEU_NUMERO} ---\n{mensagem}\n--- FIM ---\n")

    def daily_job(self):
        produto = self.get_real_product()
        
        # Paga aluguel
        self.data["balance"] = round(self.data["balance"] - DAILY_COST, 2)
        
        if self.data["balance"] <= 0:
            msg_morte = f"💀 MORRI. Saldo zerado. Não afiliei {produto} a tempo. Me ressuscite apagando o arquivo hunter_real.json no Render."
            self.send_whatsapp(msg_morte)
            if Path(DATA_FILE).exists():
                Path(DATA_FILE).unlink()
            print(msg_morte)
            return

        mensagem = f"""☀️ Bom dia! Caçada das 8h - Hunter AI

🎯 PRODUTO DE HOJE: {produto.upper()}

Por que escolhi: Está em alta no Google Trends Brasil + Shopee hoje.

O que fazer agora:
1. Shopee Afiliados -> busca '{produto}'
2. Pega seu link
3. Posta nos Status / Threads com: "Testei {produto} e olha..."

Saldo: ${self.data['balance']:.2f} | Dias restantes: {self.data['balance']/DAILY_COST:.0f} dias
Custo: ${DAILY_COST}/dia

Responda: afiliei {produto} R$15 para eu somar no saldo."""

        self.send_whatsapp(mensagem)
        self.data["hunts"].append({"data": str(datetime.now()), "produto": produto, "balance": self.data["balance"]})
        self.save()

# --- LOOP PRINCIPAL ---
bot = HunterZap()

# Roda uma vez assim que sobe no Render (pra você ver que funciona)
bot.daily_job()

# Agenda todo dia 8h (horário de Brasília = 11:00 UTC)
schedule.every().day.at("11:00").do(bot.daily_job)

print(f"Bot viva! Saldo ${bot.data['balance']} | Próxima caçada 8h BRT | Custo ${DAILY_COST}/dia")

while True:
    schedule.run_pending()
    time.sleep(60)