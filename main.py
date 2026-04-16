from telethon import TelegramClient
from telethon.errors import FloodWaitError
import asyncio

# ====== CONFIG ======
api_id = 39111464
api_hash = '80a521799d5415b97b36d4b9861e2054'
group_username = -1002333824980

messages = [
    "Hello, ",
    "Kaise ho?",
    "Test message 1",
    "Test message 2"
]

delay_between_messages = 2
delete_delay = 5
# ====================

client = TelegramClient('session_name', api_id, api_hash)

async def auto_message():
    await client.start()
    
    while True:
        sent_messages = []

        for message_text in messages:
            try:
                msg = await client.send_message(group_username, message_text)
                sent_messages.append(msg)

            except FloodWaitError as e:
                print(f"Flood wait: Sleeping for {e.seconds} seconds")
                await asyncio.sleep(e.seconds)

            except Exception as e:
                print("Error:", e)

            await asyncio.sleep(delay_between_messages)

        await asyncio.sleep(delete_delay)

        for msg in sent_messages:
            try:
                await msg.delete()
            except Exception as e:
                print("Delete Error:", e)

        await asyncio.sleep(delay_between_messages)

with client:
    client.loop.run_until_complete(auto_message())
