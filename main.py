import os, telebot, requests, time

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
CITY_QUERY = "Магнитогорск"
CHANNEL_LINK = "https://t.me/newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
GROQ_KEY = os.getenv("GROQ_KEY")
DB_FILE = "magni_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def ask_groq(title, description):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = f"Напиши один четкий заголовок и краткий пересказ новости. Суммарно строго до 300 символов. Только факты. Текст: {title}. {description}"
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20).json()
        return r['choices'][0]['message']['content'].strip()
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q={CITY_QUERY}&language=ru&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, 'r') as f: done = f.read().splitlines()
    p = 0
    for a in articles:
        if p >= 2: break
        if a["url"] not in done and a["description"]:
            summary = ask_groq(a['title'], a['description'])
            if summary:
                msg = f"{summary}\n\n🏙 <a href='{CHANNEL_LINK}'>Магнитогорск</a>"
                try:
                    bot.send_message(CHANNEL_ID, msg, parse_mode='HTML')
                    with open(DB_FILE, 'a') as f: f.write(a["url"] + "\n")
                    p += 1
                    time.sleep(5)
                except: pass

if __name__ == "__main__":
    run()
