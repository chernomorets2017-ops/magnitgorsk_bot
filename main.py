import os
import telebot
import requests
from bs4 import BeautifulSoup
import time
from openai import OpenAI

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
DEEPSEEK_API_KEY = "sk-8d8ec9586c6745e6bf11e438539533db"
DB_FILE = "magni_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def get_processed_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: 
        return f.read().splitlines()[-150:]

def save_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        text = ' '.join([p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 40])
        return text[:2000]
    except: return None

def smart_trim(text, limit):
    if len(text) <= limit: return text
    trimmed = text[:limit]
    last_dot = trimmed.rfind('.')
    return trimmed[:last_dot + 1] if last_dot != -1 else trimmed

def ai_rewrite(title, text):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты редактор Магнитогорска. Пиши кратко, до 300 симв."},
                {"role": "user", "content": f"Перескажи кратко (до 300 зн). Заголовок жирным. Тема: {title}\nТекст: {text}"}
            ],
            max_tokens=400,
            temperature=0.6
        )
        return response.choices[0].message.content
    except: return None

def run():
    query = 'Магнитогорск OR "Челябинская область" OR ММК'
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&pageSize=50&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        articles = r.json().get("articles", [])
        db = get_processed_links()
        posted = 0
        for a in articles:
            if posted >= 2: break
            l = a["url"]
            title = a.get("title", "")
            if l not in db:
                raw = get_full_text(l)
                if not raw or len(raw) < 200: continue
                txt = ai_rewrite(title, raw)
                if not txt: continue
                footer = "\n\n[🏙 newsmagni](https://t.me/newsmagni)"
                final_text = smart_trim(txt, 1000 - len(footer)) + footer
                img = a.get("urlToImage")
                try:
                    if img: bot.send_photo(CHANNEL_ID, img, caption=final_text, parse_mode='Markdown')
                    else: bot.send_message(CHANNEL_ID, final_text, parse_mode='Markdown')
                    save_link(l)
                    posted += 1
                    time.sleep(10)
                except: continue
    except: pass

if __name__ == "__main__":
    run()
