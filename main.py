import os, telebot, requests, time
import google.generativeai as genai

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
GEMINI_KEY = os.getenv("GEMINI_KEY")
DB_FILE = "magni_links.txt"

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)

def run():
    url = f"https://newsapi.org/v2/everything?q=Магнитогорск OR ММК&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=20).json()
        if r.get("status") != "ok": return
        articles = r.get("articles", [])
        if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
        with open(DB_FILE, 'r') as f: done = f.read().splitlines()
        posted = 0
        for a in articles:
            if posted >= 2: break
            link = a["url"]
            if link not in done:
                try:
                    res = model.generate_content(f"Напиши новостной пост. Заголовок жирным. Эмодзи обязательны. Инфо: {a['title']} {a['description']}")
                    txt = res.text.replace("**", "<b>").replace("*", "")
                    msg = f"{txt}\n\n<a href='https://t.me/newsmagni'>🏙 newsmagni</a>"
                    if a.get("urlToImage"): bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg[:1024], parse_mode='HTML')
                    else: bot.send_message(CHANNEL_ID, msg[:4096], parse_mode='HTML')
                except Exception as e:
                    print(f"AI Error: {e}")
                    continue
                with open(DB_FILE, 'a') as f: f.write(link + "\n")
                posted += 1
                time.sleep(5)
    except: pass

if __name__ == "__main__":
    run()
