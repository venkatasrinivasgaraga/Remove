import os
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = '22648485'
API_HASH = '8a714c643f86acb3d07a2baa4831f95b'
BOT_TOKEN = '7846507681:AAGEhlMgStbUY5mb9G-3fjhicGfrCZOJRwI'

# Words to remove from PDF file names
DEFAULT_REMOVE_WORDS = ["1074804932", "1077880102"]

bot = Client("pdf_filename_cleaner_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("Send me a PDF, and I’ll clean the file name by removing default numbers.")

@bot.on_message(filters.document & filters.private)
async def handle_pdf(client, message: Message):
    original_path = await message.download()
    original_name = message.document.file_name

    cleaned_name = original_name
    for word in DEFAULT_REMOVE_WORDS:
        cleaned_name = cleaned_name.replace(word, "")
    
    cleaned_name = cleaned_name.replace("__", "_").strip("_").strip()
    cleaned_path = f"cleaned_{cleaned_name}"

    os.rename(original_path, cleaned_path)

    await message.reply_document(document=cleaned_path, caption="Here is your renamed PDF.")

    os.remove(cleaned_path)

bot.run()
