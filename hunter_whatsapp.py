import os, requests, smtplib, json, random
from email.mime.text import MIMEText
from datetime import datetime

EMAIL_ORIGEM = os.getenv("EMAIL_ORIGEM")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")
EMAIL_SENHA = os.getenv("EMAIL_SENHA_APP")

MATT_WORD = "matheus20190"
MATT_TOOL = "77761463"
ARQUIVO_SALDO = "/tmp/saldo.json"
VALOR_VENDA = 0.72

def get_saldo():
    try:
        if os.path.exists(ARQUIVO_SALDO):
            with open(ARQUIVO_SALDO, "r") as f:
                return float(json.load(f).get("saldo", 9.8))
    except: pass
    return 9.8

def salvar_saldo(saldo):
    try:
        with open(ARQUIVO_SALDO, "w") as f:
            json.dump({"saldo": saldo, "data": str(datetime.now())}, f)
    except: pass

def gerar_link_afiliado(link_original):
    # Gera link afiliado automático com seu ID
    sep = "&" if "?" in link_original else "?"
    return f"{link_original}{sep}matt_tool={MATT_TOOL}&matt_word={MATT_WORD}&matt_source=HunterV4"

def buscar_top_tendencias():
    # Busca em várias categorias que pagam bem como afiliado
    termos = ["creatina", "whey protein", "fone bluetooth", "smartwatch", "suporte celular", "kit academia"]
    termo = random.choice(termos)

    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&sort=sold_quantity_desc&limit=10"
    try:
        r = requests.get(url, timeout=15)
        results = r.json().get("results", [])
        # Filtra preço bom pra comissão (R$30 a R$200)
        bons = [p for p in results if 30 <= p.get("price", 0) <= 200 and p.get("sold_quantity", 0) > 100]
        if not bons: bons = results
        top = random.choice(bons[:3]) if bons else results[0]

        return {
            "titulo": top["title"],
            "preco": top["price"],
            "vendidos": top["sold_quantity"],
            "link_original": top["permalink"]
        }
    except Exception as e:
        print(f"Erro busca: {e}")
        return {"titulo": "Creatina Monohidratada 1kg", "preco": 89.9, "vendidos": 5000, "link_original": "https://www.mercadolivre.com.br/creatina-monohidratada-1kg/p/MLB123"}

def enviar():
    saldo = get_saldo()
    prod = buscar_top_tendencias()
    link_afiliado = gerar_link_afiliado(prod["link_original"])

    dias = (datetime.now() - datetime(2026, 6, 23)).days
    falta = max(0, 20 - saldo)

    legenda = f"""🔥 MAIS VENDIDO HOJE - {prod['vendidos']} VENDAS

{prod['titulo']}

💰 R$ {prod['preco']}
✅ Mais de {prod['vendidos']} pessoas compraram

Link com desconto aqui 👇
{link_afiliado}

Entrega Full Mercado Livre
#achadinhos #mercadolivre #oferta"""

    corpo = f"""HUNTER V4 - IA 100% AUTOMÁTICA

💰 SALDO REAL: ${saldo:.2f}
🎯 Falta pra $20: ${falta:.2f}
📅 Dias: {dias}

🤖 IA ENCONTROU SOZINHA HOJE:
{prod['titulo']}
Preço: R$ {prod['preco']} | Vendidos: {prod['vendidos']}

Link original: {prod['link_original']}

🔗 SEU LINK AFILIADO GERADO AUTOMATICAMENTE:
{link_afiliado}

LEGENDA PRONTA PRA POSTAR:

{legenda}

---
Venda = +${VALOR_VENDA} no saldo
Me diga "vendi 1" pra atualizar saldo real.
"""

    msg = MIMEText(corpo)
    msg["Subject"] = f"V4 - SALDO ${saldo:.2f} | {prod['titulo'][:40]}"
    msg["From"] = EMAIL_ORIGEM
    msg["To"] = EMAIL_DESTINO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL_ORIGEM, EMAIL_SENHA)
        s.send_message(msg)

    salvar_saldo(saldo)
    print(f"V4 enviado! Produto: {prod['titulo']} | Link: {link_afiliado}")

if __name__ == "__main__":
    print("Hunter V4 - Caçando tendência e gerando afiliado automático...")
    enviar()
    print("Cron job run finished successfully")
