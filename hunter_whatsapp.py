def buscar_tendencia():
    try:
        print("Hunter V5 - Caçando tendência e gerando afiliado automático...")
        termos = ["fone bluetooth", "smartwatch", "air fryer", "cadeira gamer", "whey protein", "tenis nike", "tv box", "moto g"]
        random.shuffle(termos)
        
        headers = {"User-Agent": "Mozilla/5.0"}
        
        for termo in termos:
            print(f"Tentando buscar: {termo}...")
            try:
                url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=10"
                r = requests.get(url, headers=headers, timeout=15).json()
                results = r.get("results", [])
                if results:
                    prod = random.choice(results)
                    titulo = prod.get("title", "Produto ML")[:100]
                    link_original = prod.get("permalink", "")
                    preco = prod.get("price", 0)
                    link_afiliado = f"{link_original}?matt_tool={ML_TOOL}&matt_word={ML_AFFILIATE}&matt_source=HunterV5"
                    print(f"ACHOU! {titulo}")
                    return {"titulo": titulo, "preco": preco, "link": link_afiliado, "termo": termo}
            except Exception as e:
                print(f"Falha no termo {termo}: {e}")
                continue
        
        print("Erro busca: Nenhum resultado para todos os termos")
        return None
        
    except Exception as e:
        print(f"Erro busca: {e}")
        return None
