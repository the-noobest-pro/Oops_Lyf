FROM python:latest

ENV VIRTUAL_ENV "/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y ffmpeg opus-tools bpm-tools
RUN python -m pip install --upgrade pip
RUN python -m pip install wheel TgCrypto
RUN python -m pip install pytgcalls==3.0.0.dev11 ffmpeg-python psutil youtube_dl requests aiofiles aiohttp
RUN python -m pip uninstall pyrogram
RUN python -m pip install git+https://github.com/pyrogram/pyrogram@master
COPY . /app
RUN chmod 777 /app
WORKDIR /app

CMD python3 main.py

# docker build -t tgcalls .
# docker run -it --rm --env-file ./envfile --name tgvc-userbot tgcalls
