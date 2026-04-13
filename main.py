import asyncio
import random
import re
import yt_dlp
import google.generativeai as genai # Gemini import
from telethon import TelegramClient, events

# ===== CONFIG =====
api_id = 39111464
api_hash = "80a521799d5415b97b36d4b9861e2054"
chat_id = "Muzan_mbt"

# ===== GEMINI SETUP =====
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GEMINI_API_KEY)

# Model configuration
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
stickers_bot1 = ["sticker1.webp","sticker2.webp","sticker3.webp","sticker4.webp","sticker5.webp"]
stickers_bot2 = ["sticker6.webp","sticker7.webp","sticker8.webp","sticker9.webp"]

# ================= AI REPLY (GEMINI) =================
async def generate_gemini_reply(user_msg):
    try:
        response = await asyncio.to_thread(chat_session.send_message, user_msg)
        full_text = response.text.strip()
        
        # Check if AI wants to send a sticker
        send_sticker = False
        if "[SEND_STICKER]" in full_text:
            send_sticker = True
            full_text = full_text.replace("[SEND_STICKER]", "").strip()
            
        return full_text, send_sticker
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Abhi thoda busy hu, baad mein baat karte hain! 😊", False

# ================= FAST DOWNLOAD =================
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

# ================= USER REPLY =================
async def handle_user_reply(event, client, bot_index):
    msg = event.raw_text
    if event.id % 2 != bot_index:
        return

    # Link Detection
    url_pattern = r"(https?://\S+)"
    match = re.search(url_pattern, msg)
    if match:
        url = match.group(0)
        await client.send_message(chat_id, "Downloading video... ⏳", reply_to=event.id)
        try:
            file_path = await download_video(url)
            await client.send_file(chat_id, file_path, caption="Ye lo download ho gaya 🎬", reply_to=event.id)
            return
        except:
            await client.send_message(chat_id, "Download nahi ho paya 😅", reply_to=event.id)
            return

    # Human delay
    await asyncio.sleep(random.randint(5, 10))
    
    # Get Gemini Reply
    reply_text, should_send_sticker = await generate_gemini_reply(msg)

    # Send Message
    try:
        await client.send_message(chat_id, reply_text, reply_to=event.id)
        
        # Send Sticker if Gemini suggested or by 15% random chance
        if should_send_sticker or random.random() < 0.15:
            sticker_list = stickers_bot1 if bot_index == 0 else stickers_bot2
            await client.send_file(chat_id, random.choice(sticker_list), reply_to=event.id)
            
    except Exception as e:
        print("Reply error:", e)

# ================= MAIN =================
async def run_bots():
    client1 = TelegramClient("session1", api_id, api_hash)
    client2 = TelegramClient("session2", api_id, api_hash)

    await client1.start()
    await client2.start()

    me1 = await client1.get_me()
    me2 = await client2.get_me()

    print("✅ Gemini Hinglish Bot + Downloader Ready")

    @client1.on(events.NewMessage(chats=chat_id, incoming=True))
    async def handler1(event):
        if event.sender_id != me1.id:
            await handle_user_reply(event, client1, 0)

    @client2.on(events.NewMessage(chats=chat_id, incoming=True))
    async def handler2(event):
        if event.sender_id != me2.id:
            await handle_user_reply(event, client2, 1)

    await client1.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(run_bots())
