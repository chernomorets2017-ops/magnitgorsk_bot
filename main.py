import os, telebot, requests, time
from openai import OpenAI

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
DEEPSEEK_API_KEY = "sk-8d8ec9586c6745e6bf11e438539533db"
DB_FILE = "magni_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def run():
    url = f"https://newsapi.org/v2/everything?q=Магнитогорск OR ММК OR 'Челябинская область'&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=20).json()
        articles = r.get("articles", [])
        
        if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
        with open(DB_FILE, 'r') as f: done = f.read().splitlines()
        
        posted = 0
        for a in articles:
            if posted >= 2: break
            link = a["url"]
            if link not in done:
                res = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "system", "content": "Ты редактор Магнитогорска. Заголовок жирным, текст кратко и по делу."},
                              {"role": "user", "content": f"{a['title']}\n{a['description']}"}]
                )
                msg = res.choices[0].message.content + f"\n\n[🏙 newsmagni](https://t.me/newsmagni)"
                
                if a.get("urlToImage"): bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg[:1024], parse_mode='Markdown')
                else: bot.send_message(CHANNEL_ID, msg[:4096], parse_mode='Markdown')
                
                with open(DB_FILE, 'a') as f: f.write(link + "\n")
                posted += 1
                time.sleep(10)
    except: pass

if __name__ == "__main__": run()
