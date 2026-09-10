import os, requests, random, urllib.parse
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
CANAL=os.getenv("TELEGRAM_CHANNEL")
termo=random.choice(["echo dot 5","jbl go 4","fire tv stick","redmi note 13","air fryer mondial"])
url=f"https://api.mercadolibre.com/sites/MLB/search?q={urllib.parse.quote(termo)}&limit=20&sort=sold_quantity_desc"
r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
print(f"STATUS: {r.status_code} - se for 200, vai postar!")
if r.status_code==200:
    for item in r.json().get("results",[])[:5]:
        if "produto.mercadolivre.com.br/MLB-" in item.get("permalink",""):
            base=item["permalink"].split("?")[0]
            link=f"{base}?matt_tool=77761463&matt_word=matheus20190&forceInApp=true"
            texto=f"🔥 TESTE 20 ITENS 🔥\n\n📦 {item['title'][:90]}\n💰 R$ {item['price']}\n\n👇 LINK QUE ABRE DIRETO 👇\n{link}"
            img=item.get("thumbnail","").replace("-I.jpg","-O.jpg")
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id":CANAL,"photo":img,"caption":texto})
            print("POSTOU!")
            break
