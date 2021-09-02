import os
import asyncio
from pytgcalls import GroupCallFactory
from pyrogram import Client, filters
from pyrogram.types import Message


self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

GROUP_CALLS = {}

@Client.on_message(self_or_contact_filter
                   & filters.command("vidstream", prefixes="!"))
async def vidstream(client, m: Message):
    if len(m.command) < 2:
        op = 0.81
    else:
        op = m.text.split(maxsplit=2)[1]
    group_call_factory = GroupCallFactory(client, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM)
    replied = m.reply_to_message
    if not replied:
        await m.reply("`Gib Something to Stream`")
    elif replied.video or replied.document:
        lel = await m.reply("`Downloading...`")
        chat_id = m.chat.id
        try:
            huehue = await client.download_media(m.reply_to_message)
            await lel.edit("`Converting...`")
            os.system(f'ffmpeg -i "{huehue}" -vn -f s16le -ac 2 -ar 48000 -acodec pcm_s16le -filter:a "atempo={op}" vid-{chat_id}.raw -y')
        except Exception as e:
            await lel.edit(f"Error - `{e}`")
        await asyncio.sleep(5)
        try:
            group_call = group_call_factory.get_file_group_call(f'vid-{chat_id}.raw')
            await group_call.start(chat_id)
            await group_call.set_video_capture(huehue)
            GROUP_CALLS[chat_id] = group_call
            await lel.edit("`Started !`")
        except Exception as e:
            await lel.edit(f"Error -- `{e}`")
    else:
        await m.reply("`Gib Something to Stream`")

@Client.on_message(self_or_contact_filter
                   & filters.command("stopvid", prefixes="!"))
async def stopvid(client, m: Message):
    chat_id = m.chat.id
    try:
        await GROUP_CALLS[chat_id].stop()
        await m.reply("`Stopped !`")
    except Exception as e:
        await m.reply(f"Error - `{e}`")
