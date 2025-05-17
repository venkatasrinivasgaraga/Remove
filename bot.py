import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified

API_ID = '22648485'
API_HASH = '8a714c643f86acb3d07a2baa4831f95b'
BOT_TOKEN = '7846507681:AAGEhlMgStbUY5mb9G-3fjhicGfrCZOJRwI'

# Words to replace
TARGET_WORDS = ["1074804932", "1077880102", "1893104473"]
REPLACEMENT = "@Gate_Sena"

bot = Client("pdf_autorename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

THUMB_DIR = "downloads/thumbs"
os.makedirs(THUMB_DIR, exist_ok=True)

def get_user_thumb(user_id):
    path = os.path.join(THUMB_DIR, f"{user_id}.jpg")
    return path if os.path.exists(path) else None

def human_readable_size(size, decimal_places=2):
    for unit in ['B','KB','MB','GB']:
        if size < 1024:
            return f"{size:.{decimal_places}f}{unit}"
        size /= 1024
    return f"{size:.{decimal_places}f}TB"

async def progress(current, total, message, start_time):
    elapsed_time = time.time() - start_time
    percentage = current * 100 / total
    speed = human_readable_size(current / elapsed_time) if elapsed_time > 0 else "0B/s"
    bar = f"[{'=' * int(percentage / 10)}{' ' * (10 - int(percentage / 10))}]"
    try:
        await message.edit_text(
            f"**Progress**\n{bar} {percentage:.2f}%\n"
            f"Downloaded: {human_readable_size(current)} / {human_readable_size(total)}\n"
            f"Speed: {speed}"
        )
    except MessageNotModified:
        pass

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "**Welcome!**\n\n"
        "Send me a PDF and I’ll rename it by replacing numbers with `@Gate_Sena`, show progress, and apply your thumbnail.\n\n"
        "**Commands:**\n"
        "`/delthumb` – Delete your saved thumbnail\n"
        "Send any image to set as your thumbnail."
    )

@bot.on_message(filters.command("delthumb"))
async def del_thumb(client, message: Message):
    user_thumb = get_user_thumb(message.from_user.id)
    if user_thumb:
        os.remove(user_thumb)
        await message.reply("✅ Thumbnail deleted.")
    else:
        await message.reply("❌ No thumbnail was set.")

@bot.on_message(filters.photo & filters.private)
async def save_thumb(client, message: Message):
    path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await message.download(file_name=path)
    await message.reply("✅ Thumbnail saved successfully! It will be used for all future files.")

@bot.on_message(filters.document & filters.private)
async def auto_rename_pdf(client, message: Message):
    doc = message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await message.reply("Only PDF files are supported.")
        return

    progress_msg = await message.reply("Downloading...")
    start_time = time.time()
    file_path = await message.download(progress=lambda c, t: progress(c, t, progress_msg, start_time))

    # Replace words
    cleaned_name = doc.file_name
    for word in TARGET_WORDS:
        cleaned_name = cleaned_name.replace(word, REPLACEMENT)

    cleaned_name = cleaned_name.replace("__", "_").strip("_").strip()
    cleaned_path = f"cleaned_{name}"
    os.rename(file_path, cleaned_path)

    await progress_msg.edit("Uploading...")
    thumb_path = get_user_thumb(message.from_user.id)
    start_time = time.time()

    await message.reply_document(
        document=cleaned_path,
        thumb=thumb_path,
        caption=f"Here is your renamed PDF: `{cleaned_name}`",
        progress=lambda c, t: progress(c, t, progress_msg, start_time)
    )

    await progress_msg.delete()
    os.remove(cleaned_path)

bot.run()
