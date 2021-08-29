import os
from pytgcalls import GroupCallFactory
from pyrogram import Client, filters
from pyrogram.types import Message


self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

group_call_factory = GroupCallFactory(client, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM)


@Client.on_message(self_or_contact_filter
                   & filters.command("vidstream", prefixes="!"))
async def vidstream(client, m: Message):
    replied = m.reply_to_message
    if not replied:
        await m.reply("`Gib Something to Stream`")
    elif replied.video or replied.document:
        lel = await m.reply("`Downloading & Converting`")
        chat_id = m.chat.id
        try:
            huehue = await client.download_media(m.reply_to_message)
            os.system('ffmpeg -i huehue -vn -f s16le -ac 2 -ar 48000 -acodec pcm_s16le f"vid-{chat_id}.raw" -y')
        except Exception as e:
            await lel.edit(f"Error - `{e}`")
        try:
            group_call = group_call_factory.get_file_group_call(f"/app/vid-{chat_id}.raw")
            await group_call.start(chat_id)
            await group_call.set_video_capture(huehue)
            await lel.edit("`Started !`")
        except Exception as e:
            await lel.edit(f"Error -- `{e}`")
    else:
        await m.reply("`Gib Something to Stream`")
