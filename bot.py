import os
import time
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified

API_ID = '25956970'
API_HASH = '5fb73e6994d62ba1a7b8009991dd74b6'
BOT_TOKEN = '7652012423:AAEQQ_DD-suI3HH_TDxhFpZfI28W9kn-Xcs'

TARGET_WORDS = ["1074804932", "1077880102", "1893104473"]
FILENAME_REPLACEMENT = "Gate_Sena"
CAPTION_REPLACEMENT = "@Gate_Sena"
THUMB_DIR = "downloads/thumbs"
os.makedirs(THUMB_DIR, exist_ok=True)

bot = Client("pdf_autorename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_user_thumb(user_id):
    path = os.path.join(THUMB_DIR, f"{user_id}.jpg")
    return path if os.path.exists(path) else None

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB']:
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
            f"Progress\n{bar} {percentage:.2f}%\n"
            f"Downloaded: {human_readable_size(current)} / {human_readable_size(total)}\n"
            f"Speed: {speed}"
        )
    except MessageNotModified:
        pass

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "Welcome!\n\n"
        "Send a PDF and I will:\n"
        "- Rename file by replacing target words and @bijzli with Gate_Sena (in file)\n"
        "- Replace @bijzli with @Gate_Sena in caption\n"
        "- Show progress and use your custom thumbnail\n\n"
        "Commands:\n"
        "/delthumb – Delete saved thumbnail\n"
        "Send a photo to set your thumbnail"
    )

@bot.on_message(filters.command("delthumb"))
async def del_thumb(client, message: Message):
    path = get_user_thumb(message.from_user.id)
    if path:
        os.remove(path)
        await message.reply("✅ Thumbnail deleted.")
    else:
        await message.reply("❌ No thumbnail set.")

@bot.on_message(filters.photo & filters.private)
async def save_thumb(client, message: Message):
    path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await message.download(file_name=path)
    await message.reply("✅ Thumbnail saved successfully.")

@bot.on_message(filters.document & filters.private)
async def auto_rename_pdf(client, message: Message):
    doc = message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await message.reply("Only PDF files are supported.")
        return

    progress_msg = await message.reply("Downloading...")
    start_time = time.time()
    file_path = await message.download(progress=lambda c, t: progress(c, t, progress_msg, start_time))

    # Replace target words and @bijzli in original filename (no @ in filenames)
    cleaned_name = doc.file_name
    for word in TARGET_WORDS:
        cleaned_name = cleaned_name.replace(word, FILENAME_REPLACEMENT)
    cleaned_name = re.sub(r"@bijzli", FILENAME_REPLACEMENT, cleaned_name, flags=re.IGNORECASE)

    # Rename file locally
    cleaned_path = os.path.join(os.path.dirname(file_path), cleaned_name)
    os.rename(file_path, cleaned_path)

    thumb_path = get_user_thumb(message.from_user.id)

    await progress_msg.edit("Uploading...")
    start_time = time.time()

    # Replace @bijzli with @Gate_Sena in caption
    original_caption = message.caption or ""
    updated_caption = re.sub(r"@bijzli", CAPTION_REPLACEMENT, original_caption, flags=re.IGNORECASE)

    await message.reply_document(
        document=cleaned_path,
        thumb=thumb_path,
        caption=updated_caption,
        progress=lambda c, t: progress(c, t, progress_msg, start_time)
    )

    await progress_msg.delete()
    os.remove(cleaned_path)

bot.run()
