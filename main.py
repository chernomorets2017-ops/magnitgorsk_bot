import os, telebot, requests, time
from bs4 import BeautifulSoup

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
CITY_QUERY = "Магнитогорск"
CHANNEL_LINK = "https://t.me/newsmagni"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")
DB_FILE = "magni_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav']): s.decompose()
        text = ' '.join([p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 50])
        return text[:3000]
    except: return None

def ask_groq(title, text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = f"Ты редактор новостей. Сделай краткий, дерзкий пересказ статьи. 1. Яркий заголовок жирным капсом с эмодзи. 2. Суть новости в 2 коротких абзаца. 3. Закончи мысль точкой. Текст: {title}. {text}"
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.6
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25).json()
        return r['choices'][0]['message']['content'].strip()
    except: return None

def run():
    url = f"https://newsapi.org/v2/everything?q={CITY_QUERY}&sortBy=publishedAt&pageSize=10&language=ru&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, 'r', encoding='utf-8') as f: done = f.read().splitlines()
    
    p = 0
    for a in articles:
        if p >= 2: break
        if a["url"] not in done and a["title"] not in done:
            full_text = get_full_text(a["url"])
            source_text = full_text if full_text and len(full_text) > 300 else (a.get('description') or a['title'])
            
            res = ask_groq(a['title'], source_text)
            if not res: continue
            
            footer = f"\n\n🏙 <a href='{CHANNEL_LINK}'>Магнитогорск</a>"
            final_msg = res[:950] + footer
            
            try:
                if a.get("urlToImage"):
                    bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=final_msg, parse_mode='HTML')
                else:
                    bot.send_message(CHANNEL_ID, final_msg, parse_mode='HTML', disable_web_page_preview=True)
                with open(DB_FILE, 'a', encoding='utf-8') as f:
                    f.write(a["url"] + "\n")
                    f.write(a["title"] + "\n")
                p += 1
                time.sleep(15)
            except: continue

if __name__ == "__main__":
    run()
