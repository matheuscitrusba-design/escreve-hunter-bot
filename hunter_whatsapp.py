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

# --- SERVIDOR WEB PARA O RENDER FUNCIONAR ---
def start_web_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hunter Bot - ONLINE")
        def log_message(self, format, *args):
            return
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(("0.0.0.0", port), Handler)
    httpd.serve_forever()

Thread(target=start_web_server, daemon=True).start()

# --- CONFIGURACAO ---
ARQUIVO_DE_DADOS = "hunter_real.json"
CUSTO_DIARIO = float(os.getenv("CUSTO_DIARIO","0.20"))
SEU_NUMERO = os.getenv("SEU_NUMERO","557598675857")
WHATSAPP_TOKEN = os.getenv("TOKEN_DO_WHATSAPP","")
ID_DE_TELEFONE_DO_WHATSAPP = os.getenv("ID_DE_TELEFONE_DO_WHATSAPP","")

class HunterZap:
    def __init__(self):
        if Path(ARQUIVO_DE_DADOS).exists():
            self.dados = json.loads(Path(ARQUIVO_DE_DADOS).read_text(encoding="utf-8"))
        else:
            self.dados = {"equilibrio":5.00,"cacas":[],"aniversario":str(datetime.now())}
            self.salvar()
        self.pytrends = TrendReq(hl='pt-BR', tz=180)

    def salvar(self):
        Path(ARQUIVO_DE_DADOS).write_text(json.dumps(self.dados, ensure_ascii=False, indent=2), encoding="utf-8")

print("Hunter Bot iniciado com sucesso! Aguardando...")
hunter = HunterZap()

# Mantem o bot vivo
while True:
    schedule.run_pending()
    time.sleep(60)
