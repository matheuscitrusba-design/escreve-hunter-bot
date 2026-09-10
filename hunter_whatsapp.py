import os, requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CANAL = os.getenv("TELEGRAM_CHANNEL")

print(f"DEBUG TOKEN existe? {bool(TOKEN)}")
print(f"DEBUG CANAL: {CANAL}")
print("Hunter V5 TESTE - enviando mensagem fixa...")

texto = "🔥 TESTE DO HUNTER V5 🔥\nSe você tá vendo isso, o bot do Telegram está FUNCIONANDO!\nLink teste: https://mercadolivre.com.br"

try:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CANAL, "text": texto}, timeout=15)
    print(f"Telegram response: {r.text}")
except Exception as e:
    print(f"ERRO: {e}")

print("Fim teste")
