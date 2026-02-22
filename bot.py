import os
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import g4f
from telegram import Bot
import asyncio

TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHAT_ID = "-1003710522551"
SOURCE_URL = "https://www.magcity74.ru/"
BASE_URL = "https://www.magcity74.ru/"

async def get_rewrite(text):
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Сделай краткий рерайт новости. Начни с жирного заголовка. Структурируй по смыслу: {text[:2000]}"}],
        )
        return response
    except:
        return text[:1000]

async def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        r = requests.get(SOURCE_URL, headers=headers, timeout=20)
        r.raise_for_status()
    except:
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/news/' in href and any(char.isdigit() for char in href):
            full_url = href if href.startswith('http') else BASE_URL + href
            if full_url not in links:
                links.append(full_url)

    if not links:
        return

    link = links[0]

    if os.path.exists("last_news.txt"):
        with open("last_news.txt", "r") as f:
            if link in f.read():
                return

    article = Article(link)
    article.download()
    article.parse()
    
    raw_text = article.text
    if not raw_text:
        return

    img = article.top_image
    rewritten_text = await get_rewrite(raw_text)

    bot = Bot(token=TOKEN)
    
    try:
        if img and len(img) > 10:
            await bot.send_photo(chat_id=CHAT_ID, photo=img, caption=rewritten_text[:1024])
        else:
            await bot.send_message(chat_id=CHAT_ID, text=rewritten_text[:4096])
        
        with open("last_news.txt", "w") as f:
            f.write(link)
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())