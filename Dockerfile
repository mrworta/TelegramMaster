FROM alpine:latest
RUN apk update
RUN apk add python3
RUN pip3 install pika
RUN pip3 install telethon
COPY queuewalker.py .
ENTRYPOINT python3 -u ./queuewalker.py
