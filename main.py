import os, telebot, requests, time
import g4f

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
DB_FILE = "magni_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def run():
    url = f"https://newsapi.org/v2/everything?q=Магнитогорск OR ММК&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=20)
        data = r.json()
        articles = data.get("articles", [])

        if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
        with open(DB_FILE, 'r') as f: done = f.read().splitlines()

        posted = 0
        for a in articles:
            if posted >= 2: break
            link = a["url"]
            if link not in done:
                try:
                    response = g4f.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": f"Сделай краткий пост для ТГ (заголовок жирным): {a['title']}\n{a['description']}"}]
                    )
                    msg = response + f"\n\n[🏙 newsmagni](https://t.me/newsmagni)"
                except:
                    msg = f"**{a['title']}**\n\n{a['description']}\n\n[🏙 newsmagni](https://t.me/newsmagni)"
                
                if a.get("urlToImage"): bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg[:1024], parse_mode='Markdown')
                else: bot.send_message(CHANNEL_ID, msg[:4096], parse_mode='Markdown')
                
                with open(DB_FILE, 'a') as f: f.write(link + "\n")
                posted += 1
                time.sleep(5)
    except: pass

if __name__ == "__main__":
    run()
