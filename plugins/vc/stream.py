import os
import re
import subprocess

import asyncio
import ffmpeg 
import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from signal import SIGINT
from youtube_dl import YoutubeDL
from pytgcalls import GroupCall 


# Special Thanks to AsmSafone for the YTDL filter.

# Commands available only for owner and contacts

self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

GROUP_CALLS = {}
FFMPEG_PROCESSES = {}

ydl_opts = {
    "geo_bypass": True,
    "geo_bypass_country": "IN",
    "nocheckcertificate": True
    }
ydl = YoutubeDL(ydl_opts)


@Client.on_message(self_or_contact_filter & filters.command('stream', prefixes='!'))
async def stream(client, message: Message):
    input_filename = f'radio-{message.chat.id}.raw'
    radiostrt = await message.reply_text("`...`")

    process = FFMPEG_PROCESSES.get(message.chat.id)
    if process:
        try:
            process.send_signal(SIGINT)
            await asyncio.sleep(1)
        except Exception as e:
            print(e)

    if len(message.command) < 2:
        await message.reply_text('You forgot to enter a Stream URL')
        return   

    query = message.command[1]
    regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
    match = re.match(regex,query)
    if match:
        try:
            meta = ydl.extract_info(query, download=False)
            formats = meta.get('formats', [meta])
            for f in formats:
                ytstreamlink = f['url']
            station_stream_url = ytstreamlink
        except Exception as e:
            await message.reply_text(f'**⚠️ Error** \n{e}')
            print(e)
    else:
        station_stream_url = query
        print(station_stream_url)

    process = subprocess.Popen(
                  ['ffmpeg', '-i', station_stream_url, '-vn', '-f', 's16le', '-ac', '2', '-ar', '48000', '-acodec', 'pcm_s16le', '-filter:a', "atempo=1", input_filename, '-y'],
                  stdin=None,
                  stdout=None,
                  stderr=None,
                  cwd=None,
              )

    FFMPEG_PROCESSES[message.chat.id] = process
    radio_call = GroupCall(client, input_filename, path_to_log_file='')
    chat_id = message.chat.id
    if chat_id in GROUP_CALLS:
        await asyncio.sleep(1)
        await radiostrt.edit(f'📻 Started **[Live Streaming]({query})** in `{chat_id}`', disable_web_page_preview=True)
    else:
        await radiostrt.edit(f'`📻 Radio is Starting...`')
        await asyncio.sleep(3)
        await radiostrt.edit(f'📻 Started **[Live Streaming]({query})** in `{chat_id}`', disable_web_page_preview=True)
        await radio_call.start(message.chat.id)
        GROUP_CALLS[m.chat.id] = radio_call


@Client.on_message(self_or_contact_filter & filters.command('end', prefixes='!'))
async def stopradio(_, message: Message):   
    smsg = await message.reply_text(f'⏱️ Stopping...')
    radio_call = GROUP_CALLS.get(message.chat.id)
    if radio_call:
        radio_call.input_filename = ''

    process = FFMPEG_PROCESSES.get(message.chat.id)
    if process:
        try:
            process.send_signal(SIGINT)
            await asyncio.sleep(3)
        except Exception as e:
            print(e)
        await smsg.edit(f'**⏹ Stopped Streaming!** \n\nNow kindly send `!quit` to leave VC')


@Client.on_message(self_or_contact_filter & filters.command('quit', prefixes='!'))
async def leaveradio(_, message: Message):
    if chat_id in GROUP_CALLS:
        await GROUP_CALLS[m.chat.id].stop()
        GROUP_CALLS.pop(chat_id)
    else:
        return

@Client.on_message(self_or_contact_filter & filters.command('radio', prefixes='!'))
async def show_radio_help(_, m: Message):
    await m.reply_text(f"- [Some Live Stream Links Here](https://telegra.ph/Some-Radio-Links-08-17) \n- You can also use YT-LIVE URL \n\n`!stream [stream_url]`  -  __Starts Live Stream from that Link__ \n`!end`  -  __Stops the Live Stream__", disable_web_page_preview=True)
