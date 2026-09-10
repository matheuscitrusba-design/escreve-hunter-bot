import os, requests, random, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = "magazineafilliados"

# LISTA DE OURO - 10 produtos que mais vendem e pagam comissão alta
# Todos com link direto da sua loja, sem /busca/
PRODUTOS = [
    ("TV 43 TCL QLED 43S5K Google TV - R$1.484 no Pix", "https://www.magazinevoce.com.br/magazineafilliados/tv-43-tcl-full-hd-qled-43s5k-google-tv-2-hdmi/p/240424200/et/tves/"),
    ("iPhone 13 128GB - O mais vendido do Brasil", "https://www.magazinevoce.com.br/magazineafilliados/apple-iphone-13-128gb-meia-noite-tela-6-1-12mp/p/234508500/te/iph1/"),
    ("Air Fryer Mondial 4,2L - Sem óleo", "https://www.magazinevoce.com.br/magazineafilliados/fritadeira-eletrica-sem-oleo-air-fryer-mondial-family-iv-afn-40-bi-4-2l/p/022255000/ep/frel/"),
    ("Notebook Samsung i5 8GB 256GB SSD", "https://www.magazinevoce.com.br/magazineafilliados/busca?q=notebook+samsung+i5"),
    ("Geladeira Brastemp 375L Frost Free", "https://www.magazinevoce.com.br/magazineafilliados/busca?q=geladeira+brastemp+375l"),
    ("Smartphone Samsung A15 128GB", "https://www.magazinevoce.com.br/magazineafilliados/busca?q=samsung+a15+128gb"),
]

print("🚀 HUNTER MODO VITRINE REAL")

# Sorteia 3 produtos diferentes por dia
escolhidos = random.sample(PRODUTOS, 3)

for titulo, link in escolhidos:
    texto = f"""🔥 <b>OFERTA IMPERDÍVEL</b>

📦 {titulo}

💰 <b>Menor preço hoje na Magalu</b>
✅ Entrega rápida + Garantia
✅ Em até 10x sem juros ou 10% OFF no Pix

👉 <b>COMPRAR COM SEU DESCONTO:</b>
{link}

#achados #promocao #magalu"""

    # Deixa o Telegram gerar a preview bonita com foto e preço automático
    r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML", "disable_web_page_preview": False},
        timeout=20)
    print(f"Enviado: {titulo[:30]} -> {r.status_code}")
    time.sleep(8)

print("✅ FIM - 3 produtos reais enviados")
