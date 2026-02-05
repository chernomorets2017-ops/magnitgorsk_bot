import os, telebot, requests, time
import google.generativeai as genai

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(BOT_TOKEN)

def run():
    url = f"https://newsapi.org/v2/everything?q=Магнитогорск&language=ru&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    for a in articles[:2]:
        res = model.generate_content(f"Напиши новостной пост с эмодзи. Заголовок жирным. Инфо: {a['title']}")
        txt = res.text.replace("**", "<b>").replace("*", "")
        msg = f"{txt}\n\n🏙 newsmagni"
        bot.send_message(CHANNEL_ID, msg, parse_mode='HTML')
        time.sleep(5)

if __name__ == "__main__":
    run()
