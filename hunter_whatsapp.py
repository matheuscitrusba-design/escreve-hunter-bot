codigo = r'''import os
import re
import time
import random
import requests

from datetime import datetime
from urllib.parse import quote


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

LINKS_BASE_VALIDOS = [
    "https://magazineluiza.onelink.me/589508454/2k218c14",
    "https://magazineluiza.onelink.me/589508454/7xvwxhco",
    "https://magazineluiza.onelink.me/589508454/u227lo53"
]

MAX_OFERTAS_POR_EXECUCAO = 3

ESPERA_MIN = 8
ESPERA_MAX = 15

CATEGORIAS = [
    "smart tv 43 qled",
    "air fryer",
    "iphone",
    "celular samsung",
    "caixa de som jbl",
    "ventilador",
    "fogao 4 bocas",
    "geladeira frost free",
    "notebook",
    "microondas",
    "guarda roupa casal",
    "tenis",
    "cadeira gamer",
    "fone bluetooth",
    "smartwatch"
]

ARQUIVO_HISTORICO = "produtos_publicados.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9"
}


# ============================================================
# LOG
# ============================================================

def log(mensagem):
    agora = datetime.now().strftime("%H:%M:%S")
    print(f"[{agora}] {mensagem}")


# ============================================================
# CONFIGURAÇÃO
# ============================================================

def validar_configuracao():
    erros = []

    if not BOT_TOKEN:
        erros.append("TELEGRAM_BOT_TOKEN não configurado.")

    if not CHANNEL:
        erros.append("TELEGRAM_CHANNEL não configurado.")

    if not LINKS_BASE_VALIDOS:
        erros.append("Nenhum link de afiliado configurado.")

    if erros:
        for erro in erros:
            log(f"ERRO: {erro}")
        return False

    return True


# ============================================================
# HISTÓRICO
# ============================================================

def carregar_historico():
    if not os.path.exists(ARQUIVO_HISTORICO):
        return set()

    try:
        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:
            return {
                linha.strip()
                for linha in arquivo
                if linha.strip()
            }

    except Exception as erro:
        log(f"Falha ao carregar histórico: {erro}")
        return set()


def salvar_no_historico(produto_id):
    try:
        with open(
            ARQUIVO_HISTORICO,
            "a",
            encoding="utf-8"
        ) as arquivo:
            arquivo.write(f"{produto_id}\n")

    except Exception as erro:
        log(f"Falha ao salvar histórico: {erro}")


# ============================================================
# BUSCA DIRETA
# ============================================================

def buscar_direto(url):
    try:
        resposta = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        log(
            f"Direto: HTTP {resposta.status_code} | "
            f"{len(resposta.text)} caracteres"
        )

        if resposta.status_code == 200 and len(resposta.text) > 2000:
            return resposta.text

    except Exception as erro:
        log(f"Falha busca direta: {erro}")

    return ""


# ============================================================
# BUSCA POR JINA
# ============================================================

def buscar_jina(url):
    try:
        url_jina = "https://r.jina.ai/http://" + url.replace(
            "https://", ""
        )

        resposta = requests.get(
            url_jina,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/plain"
            },
            timeout=30
        )

        log(
            f"Jina: HTTP {resposta.status_code} | "
            f"{len(resposta.text)} caracteres"
        )

        if resposta.status_code == 200 and len(resposta.text) > 1000:
            return resposta.text

    except Exception as erro:
        log(f"Falha Jina: {erro}")

    return ""


# ============================================================
# BUSCA POR ALLORIGINS
# ============================================================

def buscar_allorigins(url):
    try:
        url_proxy = (
            "https://api.allorigins.win/raw?url="
            + quote(url, safe="")
        )

        resposta = requests.get(
            url_proxy,
            headers=HEADERS,
            timeout=30
        )

        log(
            f"AllOrigins: HTTP {resposta.status_code} | "
            f"{len(resposta.text)} caracteres"
        )

        if resposta.status_code == 200 and len(resposta.text) > 1000:
            return resposta.text

    except Exception as erro:
        log(f"Falha AllOrigins: {erro}")

    return ""


# ============================================================
# BUSCA DE PRODUTOS
# ============================================================

def buscar_produtos(termo):
    log(f"Buscando: {termo}")

    termo_url = quote(
        termo.replace(" ", "-")
    )

    url = (
        "https://www.magazineluiza.com.br/"
        f"busca/{termo_url}/"
    )

    # 1. Tenta acesso direto
    html = buscar_direto(url)

    # 2. Se o Magalu responder 403, tenta Jina
    if not html:
        log("Acesso direto falhou. Tentando Jina...")
        html = buscar_jina(url)

    # 3. Última tentativa por AllOrigins
    if not html:
        log("Jina falhou. Tentando AllOrigins...")
        html = buscar_allorigins(url)

    if not html:
        log(
            "Não foi possível obter a página do produto."
        )
        return []

    produtos = extrair_produtos(html)

    log(
        f"Produtos encontrados: {len(produtos)}"
    )

    return produtos


# ============================================================
# EXTRAÇÃO
# ============================================================

def extrair_produtos(html):
    encontrados = []

    # IDs em URLs completas
    ids = re.findall(
        r'https?://www\.magazineluiza\.com\.br/[^"\']+/p/([A-Za-z0-9_-]+)',
        html
    )

    # IDs em caminhos /p/
    if not ids:
        ids = re.findall(
            r'/p/([A-Za-z0-9_-]{5,})',
            html
        )

    ids = list(dict.fromkeys(ids))

    # Títulos
    titulos = []

    padroes_titulo = [
        r'"title":"([^"]{5,200})"',
        r'"name":"([^"]{5,200})"',
        r'"productName":"([^"]{5,200})"',
        r'<title>(.*?)</title>'
    ]

    for padrao in padroes_titulo:
        encontrados_titulos = re.findall(
            padrao,
            html,
            flags=re.IGNORECASE | re.DOTALL
        )

        titulos.extend(encontrados_titulos)

    titulos = [
        limpar_texto(t)
        for t in titulos
    ]

    titulos = [
        t for t in dict.fromkeys(titulos)
        if len(t) >= 5
    ]

    # Montagem
    for indice, produto_id in enumerate(ids[:15]):

        if indice >= len(titulos):
            continue

        titulo = titulos[indice]

        if len(titulo) < 5:
            continue

        url_produto = (
            "https://www.magazineluiza.com.br/p/"
            f"{produto_id}/"
        )

        encontrados.append({
            "id": produto_id,
            "title": titulo[:120],
            "url": url_produto
        })

    return encontrados


# ============================================================
# LIMPEZA
# ============================================================

def limpar_texto(texto):
    texto = texto.replace("\\/", "/")
    texto = texto.replace("\\u002F", "/")
    texto = texto.replace("\\\"", '"')
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


# ============================================================
# LINK DE AFILIADO
# ============================================================

def gerar_link_afiliado(produto):
    base = random.choice(
        LINKS_BASE_VALIDOS
    ).split("?")[0]

    produto_id = produto["id"]
    titulo = produto["title"]

    parametros = (
        f"?af_sub1={quote(produto_id)}"
        f"&utm_source=telegram"
        f"&utm_medium=afiliado"
        f"&utm_campaign=ofertas"
        f"&utm_term={quote(titulo[:80])}"
    )

    return base + parametros


# ============================================================
# TEXTO
# ============================================================

def montar_texto(produto, link):
    titulo = produto["title"]

    return (
        "🔥 <b>ACHADO DO DIA</b>\n\n"
        f"🛍️ <b>{titulo.upper()}</b>\n\n"
        "✅ Produto encontrado no Magalu\n"
        "⚡ Confira preço e disponibilidade\n\n"
        "👇 <b>VER PRODUTO:</b>\n"
        f"{link}\n\n"
        "⏰ Preço e estoque podem mudar sem aviso.\n\n"
        "#oferta #achados #promocao #magalu"
    )


# ============================================================
# TELEGRAM
# ============================================================

def enviar_telegram(texto):
    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    dados = {
        "chat_id": CHANNEL,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        resposta = requests.post(
            url,
            data=dados,
            timeout=20
        )

        log(
            f"Telegram: HTTP {resposta.status_code}"
        )

        if resposta.status_code == 200:
            return True

        log(
            f"Telegram respondeu: "
            f"{resposta.text[:500]}"
        )

    except requests.RequestException as erro:
        log(f"Erro Telegram: {erro}")

    return False


# ============================================================
# FILTRO
# ============================================================

def produto_valido(produto, historico):
    if not produto:
        return False

    produto_id = produto.get("id")
    titulo = produto.get("title")
    url = produto.get("url")

    if not produto_id or not titulo or not url:
        return False

    if len(titulo.strip()) < 5:
        return False

    if produto_id in historico:
        log(
            f"Produto já publicado: {produto_id}"
        )
        return False

    return True


# ============================================================
# PRINCIPAL
# ============================================================

def main():

    log("=" * 60)
    log("HUNTER DE OFERTAS V3")
    log("Sistema iniciado")
    log("=" * 60)

    if not validar_configuracao():
        log("Configuração inválida. Encerrando.")
        return

    historico = carregar_historico()

    termos = random.sample(
        CATEGORIAS,
        min(6, len(CATEGORIAS))
    )

    log(
        f"Categorias selecionadas: "
        f"{', '.join(termos)}"
    )

    enviados = 0

    for termo in termos:

        if enviados >= MAX_OFERTAS_POR_EXECUCAO:
            break

        produtos = buscar_produtos(termo)

        if not produtos:
            log(
                f"Nenhum produto confirmado para: {termo}"
            )
            continue

        random.shuffle(produtos)

        for produto in produtos:

            if enviados >= MAX_OFERTAS_POR_EXECUCAO:
                break

            if not produto_valido(
                produto,
                historico
            ):
                continue

            link = gerar_link_afiliado(produto)

            texto = montar_texto(
                produto,
                link
            )

            log(
                f"Publicando: "
                f"{produto['title'][:70]}"
            )

            if enviar_telegram(texto):

                salvar_no_historico(
                    produto["id"]
                )

                historico.add(
                    produto["id"]
                )

                enviados += 1

                log(
                    f"✅ OFERTA {enviados}/"
                    f"{MAX_OFERTAS_POR_EXECUCAO} "
                    f"PUBLICADA"
                )

                if enviados < MAX_OFERTAS_POR_EXECUCAO:

                    espera = random.randint(
                        ESPERA_MIN,
                        ESPERA_MAX
                    )

                    log(
                        f"Aguardando {espera}s..."
                    )

                    time.sleep(espera)

                break

            time.sleep(5)

    log("=" * 60)

    if enviados == 0:
        log("Nenhuma oferta publicada.")
        log(
            "Nenhum produto foi inventado "
            "como substituição."
        )
    else:
        log(
            f"FINALIZADO: {enviados} "
            f"oferta(s) publicada(s)."
        )

    log("=" * 60)


if __name__ == "__main__":
    main()
'''

caminho = "/mnt/data/hunter_whatsapp_v3.py"
with open(caminho, "w", encoding="utf-8") as f:
    f.write(codigo)

print(f"Arquivo pronto: {caminho}")
