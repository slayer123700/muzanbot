import os

class Config:
    API_ID = int(os.environ.get("API_ID", 12345)) # Default backup
    API_HASH = os.environ.get("API_HASH", "your_hash")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    CHAT_ID = os.environ.get("CHAT_ID", "Muzan_mbt")
    
    STICKERS_BOT1 = ["sticker1.webp", "sticker2.webp"]
    STICKERS_BOT2 = ["sticker6.webp", "sticker7.webp"]
    
    SYSTEM_PROMPT = """Reply in Hinglish, 1-2 lines. Natural tone. Add 1 emoji. 
    If context is funny/happy, add [SEND_STICKER] at the end."""
