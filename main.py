import asyncio
import random
import re
import yt_dlp
import google.generativeai as genai
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ================= CONFIG =================
# Replace these with your actual values
API_ID = 39111464
API_HASH = "80a521799d5415b97b36d4b9861e2054"
STRING_SESSION = "PASTE_YOUR_STRING_SESSION_HERE"  # Your generated string goes here
CHAT_ID = "Muzan_mbt"
GEMINI_API_KEY = "AIzaSyABxVlN-saTZrWsPh6fNzBmEZXCAGQfKfQ"

# ================= GEMINI SETUP =================
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 150,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="""You are a smart, professional Hinglish assistant. 
    Rules:
    - Reply in Hinglish (mix of Hindi and English).
    - Keep it short (1-2 lines).
    - Use a human-like, natural tone.
    - Always include 1 relevant emoji.
    - If the user seems very happy, excited, or funny, end your reply with the keyword [SEND_STICKER]."""
)

chat_session = model.start_chat(history=[])

# ================= STICKERS =================
stickers = ["sticker1.webp", "sticker2.webp", "sticker3.webp", "sticker4.webp", "sticker5.webp"]

# ================= AI REPLY (GEMINI) =================
async def generate_gemini_reply(user_msg):
    try:
        response = await asyncio.to_thread(chat_session.send_message, user_msg)
        full_text = response.text.strip()
        
        send_sticker = False
        if "[SEND_STICKER]" in full_text:
            send_sticker = True
            full_text = full_text.replace("[SEND_STICKER]", "").strip()
            
        return full_text, send_sticker
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Abhi thoda busy hu, baad mein baat karte hain! 😊", False

# ================= VIDEO DOWNLOADER =================
async def download_video(url):
    loop = asyncio.get_event_loop()
    def run():
        ydl_opts = {
            "outtmpl": "video.%(ext)s",
            "format": "best[ext=mp4][height<=720]/mp4",
            "quiet": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    return await loop.run_in_executor(None, run)

# ================= MAIN LOGIC =================
async def main():
    # Initializing with StringSession for easy hosting
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    
    await client.start()
    me = await client.get_me()
    print(f"✅ Bot is running as: {me.first_name}")

    @client.on(events.NewMessage(chats=CHAT_ID, incoming=True))
    async def handler(event):
        # Don't reply to yourself
        if event.sender_id == me.id:
            return

        msg = event.raw_text

        # 1. Check for links to download
        url_pattern = r"(https?://\S+)"
        match = re.search(url_pattern, msg)
        if match:
            url = match.group(0)
            status_msg = await event.reply("Downloading video... ⏳")
            try:
                file_path = await download_video(url)
                await client.send_file(CHAT_ID, file_path, caption="Ye lo download ho gaya 🎬", reply_to=event.id)
                await status_msg.delete()
                return
            except Exception as e:
                print(f"Download Error: {e}")
                await status_msg.edit("Download nahi ho paya 😅")
                return

        # 2. Process with Gemini (Human-like delay)
        await asyncio.sleep(random.randint(3, 7))
        reply_text, should_send_sticker = await generate_gemini_reply(msg)

        # 3. Send Reply
        try:
            await event.reply(reply_text)
            
            # Send random sticker or if AI suggested
            if should_send_sticker or random.random() < 0.15:
                await client.send_file(CHAT_ID, random.choice(stickers), reply_to=event.id)
        except Exception as e:
            print(f"Reply Error: {e}")

    print("✅ Bot is listening for messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
