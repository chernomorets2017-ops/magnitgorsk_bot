import os, telebot, requests, time

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
HF_TOKEN = "Hf_GDieciCdUgjABkmxcboMXsgqEOlzgmaFPs"
API_URL = "https://api-inference.huggingface.co/models/IlyaGusev/mbart_ru_sum_gazeta"
DB_FILE = "magni_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def summarize(text):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        r = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=20).json()
        return r[0]['summary_text']
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q=Магнитогорск&language=ru&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, 'r') as f: done = f.read().splitlines()
    p = 0
    for a in articles:
        if p >= 2: break
        if a["url"] not in done:
            res = summarize(f"{a['title']}. {a['description']}")
            txt = res if res else a['title']
            bot.send_message(CHANNEL_ID, f"<b>{a['title']}</b>\n\n{txt}\n\n🏙 newsmagni", parse_mode='HTML')
            with open(DB_FILE, 'a') as f: f.write(a["url"] + "\n")
            p += 1
            time.sleep(5)

if __name__ == "__main__":
    run()
