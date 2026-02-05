import os, telebot, requests, time
import google.generativeai as genai

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
GEMINI_KEY = os.getenv("GEMINI_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(BOT_TOKEN)

def run():
    url = f"https://newsapi.org/v2/everything?q=Магнитогорск&language=ru&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url).json()
        articles = r.get("articles", [])
        for a in articles[:2]:
            try:
                res = model.generate_content(f"Напиши пост. Заголовок жирным. Эмодзи. Текст: {a['title']}")
                bot.send_message(CHANNEL_ID, f"{res.text}\n\n🏙 newsmagni", parse_mode='HTML')
            except:
                bot.send_message(CHANNEL_ID, f"<b>{a['title']}</b>\n\n{a['url']}", parse_mode='HTML')
            time.sleep(5)
    except: pass

if __name__ == "__main__":
    run()
