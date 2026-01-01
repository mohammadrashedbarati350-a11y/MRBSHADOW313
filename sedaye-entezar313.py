from telethon import TelegramClient, events
import asyncio
import google.generativeai as genai
import os

# --- 1. CONFIG (Environment Variables) ---
# این مقادیر را در پنل سرور (مثل Koyeb) ست خواهیم کرد
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# کانال منبع (جایی که پیام از آن کپی می‌شود)
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL") 
# کانال مقصد (جایی که پیام نهایی فرستاده می‌شود)
DEST_CHANNEL = int(os.getenv("DEST_CHANNEL"))

# --- 2. AI SETUP ---
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. TELEGRAM CLIENT (No Proxy) ---
# در سرور خارج، تلگرام فیلتر نیست؛ پس پروکسی را حذف کردیم
client = TelegramClient('gemini_session', API_ID, API_HASH)

# --- 4. AI FUNCTION ---
def ask_gemini(text):
    try:
        # پرامپت دلخواه شما
        prompt = f"لطفاً متن زیر را با ایموجی‌های جذاب بازنویسی و راست‌چین کن:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# --- 5. AUTOMATIC HANDLER ---
@client.on(events.NewMessage(chats=SOURCE_CHANNEL)) 
async def handler(event):
    if not event.raw_text: return
    
    print(f"📩 New message from {SOURCE_CHANNEL} received.")
    
    # پردازش توسط هوش مصنوعی
    answer = ask_gemini(event.raw_text)
    
    if answer:
        # ارسال مستقیم و خودکار به کانال مقصد (بدون نیاز به تایید)
        await client.send_message(DEST_CHANNEL, answer)
        print("✅ Message auto-posted successfully!")

async def main():
    # شروع به کار ربات
    await client.start()
    print("🚀 Bot is ONLINE on Server (Auto-Mode)!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())