import requests
import aria2p
from datetime import datetime
from status import format_progress_bar
import asyncio
import os, time
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)
options = {
    "max-tries": "50",
    "retry-wait": "3",
    "continue": "true"
}

aria2.set_global_options(options)


import requests
from datetime import datetime
from status import format_progress_bar
import asyncio
import os
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import tempfile

async def download_video(url, reply_msg, user_mention, user_id):
    try:
        api = "https://api-xi-jade.vercel.app/api/download"
        res = requests.get(api, params={"url": url, "token": "TERAXBOTZ"})
        res.raise_for_status()
        data = res.json()

        if not data.get("success"):
            raise Exception(data.get("message", "Invalid Response"))

        info = data["data"]
        file_name = info["file_name"]
        video_title = file_name
        download_url = info["download_url"]
        file_size = info["file_size"]

        await reply_msg.edit_text(
            f"📥 **Downloading...**\n\n**File:** {file_name}\n**Size:** {file_size}"
        )

        temp_path = os.path.join(tempfile.gettempdir(), file_name)
        start_time = datetime.now()
        last_update_time = time.time()

        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(temp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 512):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Progress bar update every 2s
                        if time.time() - last_update_time > 2:
                            percentage = (downloaded / total) * 100
                            elapsed = (datetime.now() - start_time).total_seconds()
                            progress = format_progress_bar(
                                filename=video_title,
                                percentage=percentage,
                                done=downloaded,
                                total_size=total,
                                status="Downloading",
                                eta=(total - downloaded) / (downloaded / elapsed) if downloaded > 0 else 0,
                                speed=downloaded / elapsed if downloaded > 0 else 0,
                                elapsed=elapsed,
                                user_mention=user_mention,
                                user_id=user_id,
                                aria2p_gid=""
                            )
                            await reply_msg.edit_text(progress)
                            last_update_time = time.time()

        # Thumbnail none, since not in this API
        await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ...")
        return temp_path, None, video_title

    except Exception as e:
        logging.error(f"Download error: {e}")
        await reply_msg.reply_text(f"❌ Failed to download video:\n`{e}`")
        return None, None, None


# async def download_video(url, reply_msg, user_mention, user_id):
#     response = requests.get(f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={url}")
#     response.raise_for_status()
#     data = response.json()

#     resolutions = data["response"][0]["resolutions"]
#     fast_download_link = resolutions["Fast Download"]
#     hd_download_link = resolutions["HD Video"]
#     thumbnail_url = data["response"][0]["thumbnail"]
#     video_title = data["response"][0]["title"]

#     download = aria2.add_uris([fast_download_link])
#     start_time = datetime.now()

#     while not download.is_complete:
#         download.update()
#         percentage = download.progress
#         done = download.completed_length
#         total_size = download.total_length
#         speed = download.download_speed
#         eta = download.eta
#         elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
#         progress_text = format_progress_bar(
#             filename=video_title,
#             percentage=percentage,
#             done=done,
#             total_size=total_size,
#             status="Downloading",
#             eta=eta,
#             speed=speed,
#             elapsed=elapsed_time_seconds,
#             user_mention=user_mention,
#             user_id=user_id,
#             aria2p_gid=download.gid
#         )
#         await reply_msg.edit_text(progress_text)
#         await asyncio.sleep(2)

#     if download.is_complete:
#         file_path = download.files[0].path

#         thumbnail_path = "thumbnail.jpg"
#         thumbnail_response = requests.get(thumbnail_url)
#         with open(thumbnail_path, "wb") as thumb_file:
#             thumb_file.write(thumbnail_response.content)

#         await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ...")

#         return file_path, thumbnail_path, video_title
#     else:
#         return markup


async def upload_video(client, file_path, thumbnail_path, video_title, reply_msg, collection_channel_id, user_mention, user_id, message):
    file_size = os.path.getsize(file_path)
    uploaded = 0
    start_time = datetime.now()
    last_update_time = time.time()

    async def progress(current, total):
        nonlocal uploaded, last_update_time
        uploaded = current
        percentage = (current / total) * 100
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
        
        if time.time() - last_update_time > 2:
            progress_text = format_progress_bar(
                filename=video_title,
                percentage=percentage,
                done=current,
                total_size=total,
                status="Uploading",
                eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                speed=current / elapsed_time_seconds if current > 0 else 0,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=""
            )
            try:
                await reply_msg.edit_text(progress_text)
                last_update_time = time.time()
            except Exception as e:
                logging.warning(f"Error updating progress message: {e}")

    with open(file_path, 'rb') as file:
        collection_message = await client.send_video(
            chat_id=collection_channel_id,
            video=file,
            caption=f"✨ {video_title}\n👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ : {user_mention}\n📥 ᴜsᴇʀ ʟɪɴᴋ: tg://user?id={user_id}",
            thumb=thumbnail_path,
            progress=progress
        )
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=collection_channel_id,
            message_id=collection_message.id
        )
        await asyncio.sleep(1)
        await message.delete()

    await reply_msg.delete()
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEZdwRmJhCNfFRnXwR_lVKU1L9F3qzbtAAC4gUAAj-VzApzZV-v3phk4DQE")
    os.remove(file_path)
    os.remove(thumbnail_path)
    await asyncio.sleep(5)
    await sticker_message.delete()
    return collection_message.id
