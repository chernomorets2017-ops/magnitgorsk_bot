import requests
from bs4 import BeautifulSoup
import feedparser
import json
import hashlib
import time
from telegram import Bot
from googletrans import Translator

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL = "@newsmagni"
SIGN = '<a href="https://t.me/newsmagni">.магнитогорск.news</a>'

RSS = "https://www.verstov.info/rss.xml"

bot = Bot(BOT_TOKEN)
tr = Translator()

def load_db():
    try:
        return set(json.load(open("db.json")))
    except:
        return set()

def save_db(db):
    json.dump(list(db), open("db.json", "w"))

def get_article(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        text = ""
        article = soup.find("div", class_="fullstory")
        if article:
            text = " ".join(p.text for p in article.find_all("p"))

        img = ""
        og = soup.find("meta", property="og:image")
        if og:
            img = og["content"]

        return text[:2500], img
    except:
        return "", ""

def get_news():
    feed = feedparser.parse(RSS)
    news = []

    for e in feed.entries[:10]:
        text, img = get_article(e.link)

        if len(text) < 300:
            continue

        news.append({
            "title": e.title,
            "text": text,
            "img": img
        })
    return news

def make_hash(title):
    return hashlib.md5(title.encode()).hexdigest()

# ===== ОСНОВНОЙ БОТ =====
def main():
    db = load_db()
    news = get_news()

    for n in news:
        h = make_hash(n["title"])
        if h in db:
            continue

        title = tr.translate(n["title"], dest="ru").text
        text = tr.translate(n["text"], dest="ru").text[:1200]

        caption = f"""🏙 <b>Магнитогорск</b>

<b>{title}</b>

{text}

{SIGN}
"""

        if n["img"]:
            bot.send_photo(CHANNEL, n["img"], caption=caption, parse_mode="HTML")
        else:
            bot.send_message(CHANNEL, caption, parse_mode="HTML")

        db.add(h)
        time.sleep(10)

    save_db(db)

if __name__ == "__main__":
    main()