from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import google.generativeai as genai
import os

# تنظیمات از کویب
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")
DEST_CHANNEL = int(os.getenv("DEST_CHANNEL"))
SESSION_STRING = os.getenv("SESSION_STRING")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

pending_posts = {}

def ask_gemini(text):
    try:
        prompt = f"متن زیر را با لحنی جذاب و ایموجی بازنویسی کن:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except: return None

@client.on(events.NewMessage(chats=SOURCE_CHANNEL)) 
async def handler(event):
    if not event.raw_text: return
    answer = ask_gemini(event.raw_text)
    if answer:
        sent_msg = await client.send_message('me', f"🔹 پست پیشنهادی:\n\n{answer}\n\n1️⃣ ارسال به کانال\n2️⃣ لغو")
        pending_posts[sent_msg.id] = answer

@client.on(events.NewMessage(chats='me'))
async def approve_handler(event):
    if event.reply_to_msg_id in pending_posts:
        if event.text == '1':
            await client.send_message(DEST_CHANNEL, pending_posts[event.reply_to_msg_id])
            await event.respond("✅ ارسال شد!")
        elif event.text == '2':
            await event.respond("❌ لغو شد.")
        del pending_posts[event.reply_to_msg_id]

async def main():
    await client.start()
    if not SESSION_STRING:
        print("🔴 کپی کنید و در SESSION_STRING قرار دهید:")
        print(client.session.save())
        return
    print("🚀 ربات آنلاین شد و منتظر تایید شماست...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
