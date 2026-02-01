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
        lines = f.read().splitlines()
        if len(lines) > 100:
            with open(DB_FILE, "w") as fw:
                fw.write("\n".join(lines[-50:]))
            return lines[-50:]
        return lines

def save_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        text = ' '.join([p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 40])
        return text[:2000]
    except:
        return None

def smart_trim(text, limit):
    if len(text) <= limit: return text
    trimmed = text[:limit]
    last_dot = trimmed.rfind('.')
    return trimmed[:last_dot + 1] if last_dot != -1 else trimmed

def ai_rewrite(title, text):
    try:
        system_prompt = "Ты — редактор локальных новостей Магнитогорска. Пиши максимально кратко, по делу и без лишней воды."
        user_prompt = (
            f"Перескажи новость максимально коротко (1-2 небольших абзаца). Тема: {title}\nТекст: {text}\n\n"
            f"ПРАВИЛА:\n"
            f"1. Жирный заголовок в начале (с эмодзи).\n"
            f"2. Минимум текста, только самая суть для жителей города.\n"
            f"3. Закончи мысль на точке.\n"
            f"4. Стиль: дружелюбный городской паблик."
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.6,
            timeout=40
        )
        return response.choices[0].message.content
    except:
        return None

def format_fallback(title, text):
    header = f"🏙 **{title.upper()}**\n\n"
    sentences = [s.strip() for s in text.split('. ') if len(s) > 10]
    body = '. '.join(sentences[:2]) + '.'
    return header + body

def run():
    # Поиск по Магнитогорску и области
    query = "Магнитогорск OR Челябинская область"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&pageSize=15&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        articles = r.json().get("articles", [])
        db = get_processed_links()
        posted = 0
        for a in articles:
            if posted >= 2: break
            l = a["url"]
            title = a.get("title", "")
            if l not in db and not any(w in title.lower() for w in ['топ', 'список', 'подборка']):
                raw_content = get_full_text(l)
                if not raw_content or len(raw_content) < 200: continue
                
                final_text = ai_rewrite(title, raw_content)
                if not final_text:
                    final_text = format_fallback(title, raw_content)
                
                footer = "\n\n[📟 newsmagni](https://t.me/newsmagni)"
                final_text = smart_trim(final_text, 1010 - len(footer)) + footer
                
                img = a.get("urlToImage")
                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=final_text, parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, final_text, parse_mode='Markdown', disable_web_page_preview=True)
                    save_link(l)
                    posted += 1
                    time.sleep(15)
                except: continue
    except: pass

if __name__ == "__main__":
    run()
