import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from pytrends.request import TrendReq
import schedule

# --- 1. SERVIDOR WEB PARA O RENDER NÃO DAR ERRO ---
def start_web_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hunter Bot ONLINE - https://escreve-hunter-bot.onrender.com")
        def log_message(self, format, *args):
            return
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Servidor web na porta {port}")
    httpd.serve_forever()

Thread(target=start_web_server, daemon=True).start()

# --- 2. CONFIGURAÇÃO DO HUNTER ---
ARQUIVO_DE_DADOS = "hunter_real.json"
CUSTO_DIARIO = float(os.getenv("CUSTO_DIARIO", "0.20"))
SEU_NUMERO = os.getenv("SEU_NUMERO", "557598675857")
WHATSAPP_TOKEN = os.getenv("TOKEN_DO_WHATSAPP", "")
ID_DE_TELEFONE = os.getenv("ID_DE_TELEFONE_DO_WHATSAPP", "")

class HunterZap:
    def __init__(self):
        if Path(ARQUIVO_DE_DADOS).exists():
            self.dados = json.loads(Path(ARQUIVO_DE_DADOS).read_text(encoding="utf-8"))
        else:
            self.dados = {"equilibrio": 5.00, "cacas": [], "aniversario": str(datetime.now())}
            self.salvar()
        self.pytrends = TrendReq(hl='pt-BR', tz=180)
        print(f"Hunter iniciado. Saldo: R$ {self.dados['equilibrio']:.2f}")

    def salvar(self):
        Path(ARQUIVO_DE_DADOS).write_text(json.dumps(self.dados, ensure_ascii=False, indent=2), encoding="utf-8")

    def enviar_whatsapp(self, mensagem):
        if not WHATSAPP_TOKEN or not ID_DE_TELEFONE:
            print("SEM TOKEN/ID configurado. Mensagem:", mensagem[:100])
            return
        url = f"https://graph.facebook.com/v20.0/{ID_DE_TELEFONE}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": SEU_NUMERO,
            "type": "text",
            "text": {"body": mensagem}
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=20)
            print(f"WhatsApp enviado: {r.status_code}")
        except Exception as e:
            print(f"Erro ao enviar zap: {e}")

    def cacar_tendencia(self):
        print(f"[{datetime.now()}] Cacando tendencias...")
        try:
            trending = self.pytrends.trending_searches(pn='brazil')
            # Pega as 5 primeiras
            temas = trending[0].tolist()[:5]
            for tema in temas:
                if tema not in self.dados["cacas"]:
                    msg = f"🔥 HUNTER ACHOU OPORTUNIDADE 🔥\n\nTema em alta: *{tema}*\n\nCusto: R$ {CUSTO_DIARIO:.2f}\nSaldo: R$ {self.dados['equilibrio']:.2f}\n\nQuer que eu crie o artigo?"
                    self.enviar_whatsapp(msg)
                    self.dados["cacas"].append(tema)
                    self.dados["equilibrio"] -= CUSTO_DIARIO
                    self.salvar()
                    time.sleep(2)
            print("Caca finalizada.")
        except Exception as e:
            print(f"Erro na caca: {e}")

# --- 3. INICIA TUDO ---
hunter = HunterZap()

# Testa envio ao iniciar
hunter.enviar_whatsapp(f"✅ Hunter Bot LIVE!\nIniciado em {datetime.now().strftime('%d/%m %H:%M')}\nSaldo: R$ {hunter.dados['equilibrio']:.2f}\n\nVai cacar a cada 6 horas.")

# Agenda a cada 6 horas
schedule.every(6).hours.do(hunter.cacar_tendencia)

print("Hunter no ar! Aguardando agendamento...")
while True:
    schedule.run_pending()
    time.sleep(60)
