import os, telebot, requests, time
import google.generativeai as genai

BOT_TOKEN = "8217356191:AAFvVPFTwbACc6mZ7Y4HWwZeDVBn3V5rmLs"
CHANNEL_ID = "@newsmagni"
NEWS_API_KEY = "1b34822481654c9aa27b42d36bae1397"
GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)
bot = telebot.TeleBot(BOT_TOKEN)

def get_model():
    for name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
        try:
            m = genai.GenerativeModel(name)
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except: continue
    return None

def run():
    model = get_model()
    url = f"https://newsapi.org/v2/everything?q=Магнитогорск&language=ru&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    for a in articles[:2]:
        prompt = f"Напиши новостной пост с эмодзи. Заголовок жирным. Инфо: {a['title']}"
        if model:
            try:
                res = model.generate_content(prompt)
                txt = res.text.replace("**", "<b>").replace("*", "")
                bot.send_message(CHANNEL_ID, f"{txt}\n\n🏙 newsmagni", parse_mode='HTML')
            except:
                bot.send_message(CHANNEL_ID, f"<b>{a['title']}</b>\n\n{a['url']}", parse_mode='HTML')
        else:
            bot.send_message(CHANNEL_ID, f"<b>{a['title']}</b>\n\n{a['url']}", parse_mode='HTML')
        time.sleep(5)

if __name__ == "__main__":
    run()
