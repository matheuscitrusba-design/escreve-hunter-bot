import os, re, time, random, requests
from datetime import datetime
from urllib.parse import quote

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")
LOJA = os.getenv("LOJA_MAGALU", "magazineafilliados")

CATEGORIAS = ["smart tv 43", "air fryer", "iphone", "galaxy a54", "caixa jbl", "ventilador", "fogao", "geladeira", "notebook", "tenis nike"]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0", "Accept-Language": "pt-BR"}

def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def buscar_produtos(termo):
    termo_url = termo.replace(" ", "-")
    url = f"https://www.magazineluiza.com.br/busca/{termo_url}/"
    html = ""
    # Tenta direto (funciona no Render, falha no GitHub)
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        html = r.text
        log(f"Direto: {r.status_code} | {len(html)} chars")
    except: pass

    if len(html) < 2000:
        try:
            jina = f"https://r.jina.ai/http://www.magazineluiza.com.br/busca/{termo_url}/"
            r = requests.get(jina, headers=HEADERS, timeout=20)
            html = r.text
            log(f"Jina: {r.status_code} | {len(html)} chars")
        except: pass

    # EXTRAÇÃO CORRETA - pega slug + code juntos, não separado
    produtos = []
    matches = re.findall(r'/p/([a-z0-9-]+)/([a-z0-9]{7,10})/', html)
    vistos = set()
    for slug, code in matches:
        if code in vistos or len(slug) < 5: continue
        vistos.add(code)
        # Filtra slug que não é produto (ex: cliente, carrinho)
        if any(x in slug for x in ["cliente", "carrinho", "busca", "login"]): continue
        produtos.append({"slug": slug, "code": code, "title": slug.replace("-", " ").title(), "id": code})

    log(f"Produtos reais achados: {len(produtos)}")
    return produtos[:5]

def validar(link):
    try:
        r = requests.get(link, headers=HEADERS, timeout=15)
        return "produto nao foi encontrado" not in r.text.lower() and r.status_code == 200
    except: return False

def enviar(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHANNEL, "text": texto, "parse_mode": "HTML"}, timeout=20)
    log(f"Telegram {r.status_code}")
    return r.status_code == 200

def main():
    log("=== HUNTER V3 CORRIGIDO ===")
    termos = random.sample(CATEGORIAS, 5)
    enviados = 0
    for termo in termos:
        if enviados >= 3: break
        for p in buscar_produtos(termo):
            # LINK HONESTO: slug + code REAL, não onelink fixo
            link = f"https://www.magazinevoce.com.br/{LOJA}/{p['slug']}/p/{p['code']}/"
            if not validar(link):
                log(f"Oops detectado, pulando {p['title']}")
                continue
            texto = f"🔥 <b>{p['title'].upper()}</b>\n\n✅ Link validado sem Oops\n👇 COMPRAR:\n{link}\n\n#oferta"
            log(f"Publicando {p['title']}")
            if enviar(texto):
                enviados += 1
                time.sleep(random.randint(8,15))
                break
    log(f"FIM: {enviados} enviados")
    if enviados == 0:
        log("NENHUM PRODUTO INVENTADO - Isso é certo, melhor não enviar do que enviar frigobar como iphone")

if __name__ == "__main__":
    main()
