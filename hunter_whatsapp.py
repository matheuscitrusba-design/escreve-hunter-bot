```python
import os
import re
import json
import time
import random
import hashlib
import requests

from datetime import datetime
from urllib.parse import quote, urljoin


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

# Seus links-base de afiliado
LINKS_BASE_VALIDOS = [
    "https://magazineluiza.onelink.me/589508454/2k218c14",
    "https://magazineluiza.onelink.me/589508454/7xvwxhco",
    "https://magazineluiza.onelink.me/589508454/u227lo53"
]

# Quantidade máxima de ofertas publicadas por execução
MAX_OFERTAS_POR_EXECUCAO = 3

# Tempo entre publicações
ESPERA_MIN = 8
ESPERA_MAX = 15

# Categorias pesquisadas
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

# Evita publicar novamente o mesmo produto
ARQUIVO_HISTORICO = "produtos_publicados.txt"


# ============================================================
# HEADERS
# ============================================================

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
# VALIDAÇÕES
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
# ID ÚNICO
# ============================================================

def gerar_id_interno(titulo, url):
    """
    Cria um identificador determinístico.
    O mesmo produto não terá IDs aleatórios diferentes.
    """

    base = f"{titulo}|{url}".lower().strip()

    return hashlib.sha256(
        base.encode("utf-8")
    ).hexdigest()[:16]


# ============================================================
# BUSCA DE PRODUTOS
# ============================================================

def buscar_produtos(termo):
    """
    Tenta obter produtos reais da página de busca.

    IMPORTANTE:
    Se não encontrar dados suficientes, retorna [].
    Nunca inventa produto ou ID.
    """

    log(f"Buscando: {termo}")

    termo_url = quote(termo.replace(" ", "-"))

    url = (
        "https://www.magazineluiza.com.br/"
        f"busca/{termo_url}/"
    )

    try:
        resposta = requests.get(
            url,
            headers=HEADERS,
            timeout=25
        )

        log(
            f"Resposta Magalu: "
            f"{resposta.status_code} | "
            f"{len(resposta.text)} caracteres"
        )

        if resposta.status_code != 200:
            log("Página não retornou HTTP 200.")
            return []

        html = resposta.text

        if len(html) < 1000:
            log("HTML muito pequeno. Busca não confiável.")
            return []

        produtos = extrair_produtos(html)

        log(
            f"Produtos reais encontrados: "
            f"{len(produtos)}"
        )

        return produtos

    except requests.RequestException as erro:
        log(f"Erro de conexão: {erro}")
        return []

    except Exception as erro:
        log(f"Erro inesperado na busca: {erro}")
        return []


# ============================================================
# EXTRAÇÃO
# ============================================================

def extrair_produtos(html):
    """
    Tenta encontrar produtos através de diferentes padrões.

    Como páginas de e-commerce podem mudar de estrutura,
    utilizamos mais de uma estratégia.
    """

    encontrados = []

    # --------------------------------------------------------
    # Estratégia 1 — URLs de produto
    # --------------------------------------------------------

    padrao_urls = re.findall(
        r'https?://www\.magazineluiza\.com\.br/[^"\']+/p/([A-Za-z0-9_-]+)',
        html
    )

    # Remove duplicados mantendo ordem
    ids = list(dict.fromkeys(padrao_urls))

    # --------------------------------------------------------
    # Estratégia 2 — caminhos /p/ID/
    # --------------------------------------------------------

    if not ids:
        ids = re.findall(
            r'/p/([A-Za-z0-9_-]{5,})',
            html
        )

        ids = list(dict.fromkeys(ids))

    # --------------------------------------------------------
    # Títulos
    # --------------------------------------------------------

    titulos = []

    padroes_titulo = [
        r'"title":"([^"]{5,200})"',
        r'"name":"([^"]{5,200})"',
        r'"productName":"([^"]{5,200})"'
    ]

    for padrao in padroes_titulo:
        encontrados_titulos = re.findall(
            padrao,
            html
        )

        if encontrados_titulos:
            titulos.extend(encontrados_titulos)

    titulos = list(dict.fromkeys(titulos))

    # --------------------------------------------------------
    # Montagem
    # --------------------------------------------------------

    for indice, produto_id in enumerate(ids[:10]):

        if indice < len(titulos):
            titulo = titulos[indice]
        else:
            continue

        titulo = limpar_texto(titulo)

        if len(titulo) < 5:
            continue

        url_produto = (
            f"https://www.magazineluiza.com.br/p/"
            f"{produto_id}/"
        )

        encontrados.append({
            "id": produto_id,
            "title": titulo[:120],
            "url": url_produto
        })

    return encontrados


# ============================================================
# LIMPEZA DE TEXTO
# ============================================================

def limpar_texto(texto):
    texto = texto.replace("\\/", "/")
    texto = texto.replace("\\u002F", "/")
    texto = texto.replace("\\\"", '"')

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# LINK DE AFILIADO
# ============================================================

def gerar_link_afiliado(produto):
    """
    Usa um dos links-base reais.

    O produto precisa ter sido encontrado de verdade.
    """

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
# TEXTO DA OFERTA
# ============================================================

def montar_texto(produto, link):
    titulo = produto["title"]

    return (
        "🔥 <b>OFERTA ENCONTRADA!</b>\n\n"
        f"🛍️ <b>{titulo.upper()}</b>\n\n"
        "✅ Produto encontrado no Magalu\n"
        "✅ Link de compra\n"
        "⚡ Consulte preço e disponibilidade\n\n"
        "👇 <b>VER OFERTA:</b>\n"
        f"{link}\n\n"
        "⏰ O preço pode mudar a qualquer momento.\n\n"
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
            f"Telegram: "
            f"HTTP {resposta.status_code}"
        )

        if resposta.status_code == 200:
            return True

        log(
            f"Resposta Telegram: "
            f"{resposta.text[:500]}"
        )

        return False

    except requests.RequestException as erro:
        log(f"Erro Telegram: {erro}")
        return False


# ============================================================
# FILTRO DE PRODUTOS
# ============================================================

def produto_valido(produto, historico):
    if not produto:
        return False

    produto_id = produto.get("id")
    titulo = produto.get("title")
    url = produto.get("url")

    # Precisa possuir dados reais
    if not produto_id:
        return False

    if not titulo:
        return False

    if not url:
        return False

    # Título muito pequeno
    if len(titulo.strip()) < 5:
        return False

    # Não publicar novamente
    if produto_id in historico:
        log(
            f"Produto já publicado: "
            f"{produto_id}"
        )

        return False

    return True


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    log("=" * 60)
    log("HUNTER DE OFERTAS V2")
    log("Sistema iniciado")
    log("=" * 60)

    if not validar_configuracao():
        log("Configuração inválida. Encerrando.")
        return

    historico = carregar_historico()

    # Sorteia categorias para não fazer sempre
    # exatamente a mesma sequência.
    termos = random.sample(
        CATEGORIAS,
        min(6, len(CATEGORIAS))
    )

    log(
        f"Categorias selecionadas: "
        f"{', '.join(termos)}"
    )

    enviados = 0

    # --------------------------------------------------------
    # BUSCA
    # --------------------------------------------------------

    for termo in termos:

        if enviados >= MAX_OFERTAS_POR_EXECUCAO:
            break

        produtos = buscar_produtos(termo)

        if not produtos:
            log(
                f"Nenhum produto confirmado "
                f"para: {termo}"
            )
            continue

        # Embaralha levemente os resultados
        # para evitar sempre o primeiro.
        random.shuffle(produtos)

        for produto in produtos:

            if enviados >= MAX_OFERTAS_POR_EXECUCAO:
                break

            if not produto_valido(
                produto,
                historico
            ):
                continue

            # Gera link somente depois de
            # confirmar produto real.
            link = gerar_link_afiliado(
                produto
            )

            texto = montar_texto(
                produto,
                link
            )

            log(
                f"Preparando publicação: "
                f"{produto['title'][:70]}"
            )

            enviado = enviar_telegram(
                texto
            )

            if enviado:

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
                        f"Aguardando "
                        f"{espera}s..."
                    )

                    time.sleep(espera)

                break

            else:
                log(
                    "Falha ao publicar. "
                    "Tentando próximo produto."
                )

                time.sleep(5)

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    log("=" * 60)

    if enviados == 0:
        log(
            "Nenhuma oferta publicada."
        )
        log(
            "Nenhum produto foi inventado "
            "como substituição."
        )

    else:
        log(
            f"FINALIZADO: "
            f"{enviados} oferta(s) publicada(s)."
        )

    log("=" * 60)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
```
