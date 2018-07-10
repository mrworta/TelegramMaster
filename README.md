# TelegramMaster
Telegram RabbitMQ worker (for sending notifications to a channel).

# TL;DR
This container needs the following environment variables to work.

1) Telegram API Config ( get from https://my.telegram.org/ ):

TEL_API  = Telegram API ID 

TEL_NAME = Telegram App Short Name

TEL_HASH = Telegram API HASH

2) Source Phone Number

TEL_TEL = Telegram (Sender) Phone Number

3) Channel URL for the channel you created
(( This is the default value, if none is specified in the message ))

TEL_CHAN = "t.me/xxx"
