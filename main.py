import asyncio
import random


# ==========================
# CONFIG
# ==========================

API_ID = 16608386
API_HASH = "7d28fcd5000788b96071886d658be92b"

DELAY = 2
DELETE_AFTER = 4   # delete messages after this many

# ==========================
# START CLIENT
# ==========================

app = Client("random", api_id=API_ID, api_hash=API_HASH)

running = False


# ==========================
# RANDOM MESSAGE COMMAND
# ==========================

@app.on_message(filters.command("s") & filters.me)
async def start_random(client, message):
    global running

    if running:
        await message.reply("⚠️ Already running")
        return

    try:
        text = message.text.split(" ", 1)[1]
        msg_list = [x.strip() for x in text.split(",") if x.strip()]
    except:
        await message.reply("Usage:\n/s msg1, msg2, msg3")
        return

    running = True
    await message.reply("✅ Random sending started")

    sent_messages = []

    while running:
        msg = random.choice(msg_list)

        m = await message.reply(msg)
        sent_messages.append(m.id)

        # delete after 10 messages
        if len(sent_messages) >= DELETE_AFTER:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=sent_messages,
                revoke=True
            )
            sent_messages.clear()

        await asyncio.sleep(DELAY)


# ==========================
# STOP COMMAND
# ==========================

@app.on_message(filters.command("stop") & filters.me)
async def stop_random(client, message):
    global running
    running = False
    await message.reply("🛑 Random sending stopped")


# ==========================
# RUN

app.run()
