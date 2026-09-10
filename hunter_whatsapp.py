def caçar_produto():
    termos = ["creatina 1kg", "whey protein", "fone bluetooth", "smartwatch", "air fryer"]
    termo = random.choice(termos)
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=10"
    r = requests.get(url).json()
    for item in r.get("results", []):
        permalink = item.get("permalink") # LINK REAL
        if permalink:
            # Link afiliado CORRETO - pega o link real e adiciona seus códigos
            separador = "&" if "?" in permalink else "?"
            link_afiliado = f"{permalink}{separador}matt_tool={MATT_TOOL}&matt_word={MATT_WORD}"
            return {
                "titulo": item["title"],
                "preco": item["price"],
                "link": link_afiliado,
                "link_original": permalink,
                "vendidos": item.get("sold_quantity", 0)
            }
    return None
