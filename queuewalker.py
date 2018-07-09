#!/usr/bin/python3
import pika
import time
import os
from telethon import TelegramClient

for a in os.environ: print('Var: ', a, 'Value: ', os.getenv(a))
INIT_DELAY=3 # delay in seconds
WORK_DIR='/opt/telmas'

os.makedirs(WORK_DIR, exist_ok=True)
os.chdir(WORK_DIR)

REG_CODE_FILE=WORK_DIR+'/regme'

def initQueue():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RQ_HOST,port=RQ_PORT))

    channel = conn.channel() 
    channel.queue_declare(queue=RQ_Q, arguments={'x-message-ttl' : RQ_TTL})

    conn.close()

def tel_init():
    client = TelegramClient('TelMas', TEL_API, TEL_HASH)
    assert client.connect()
    if not client.is_user_authorized():
      print("You need to authorize session first.")
      print("Your phone number is %s." % TEL_TEL)
      print("Please create file %s containing the reg code. You dont need to restart the container." % REG_CODE_FILE)
      print('You can do this using kubectl or docker exec command. e.g.:')
      print('kubectl exec -ti telmas-walker-0 \'echo my-code > %s\'' % REG_CODE_FILE )

      client.send_code_request(TEL_TEL)
      while not os.path.isfile(REG_CODE_FILE): time.sleep(5)
      myf = open(REG_CODE_FILE, 'r')
      REG_CODE = myf.readline().strip()
      myf.close()
      print("Passing reg-code %s to library." % REG_CODE)
      result = client.sign_in(TEL_TEL, REG_CODE)

def tel_send(message):
    client = TelegramClient('TelMas', TEL_API, TEL_HASH)
    client.connect()
    chan = client.get_entity(TEL_CHAN_URL)
    client.send_message(chan, message)

def worker_callback(ch, method, properties, body):
    print("Got work %s " % body)
    tel_send(body.decode())
    ch.basic_ack(delivery_tag = method.delivery_tag)

def worker():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RQ_HOST,port=RQ_PORT))
    channel = conn.channel() 
    
    channel.basic_qos(prefetch_count = 1)
    channel.basic_consume(worker_callback, queue=RQ_Q)

    channel.start_consuming()

print("Starting up with init delay of %s seconds." % INIT_DELAY)
time.sleep(INIT_DELAY)    
tel_init()

if os.environ.get('RMQ_SERVICE_HOST') is None:
   print('Environment not set.')
   print('Cannot work for you. Sorry.')
   while True: time.sleep(5)

RQ_HOST=os.environ['RMQ_SERVICE_HOST']
RQ_PORT=os.environ['RMQ_SERVICE_PORT_RABBITMQ']
RQ_Q="telegram-iss"
RQ_TTL=10000 # Message TTL for queue in mseconds

TEL_API=os.environ['TEL_API']
TEL_NAME=os.environ['TEL_NAME']
TEL_HASH=os.environ['TEL_HASH']
TEL_TEL=os.environ['TEL_TEL']
TEL_CHAN_URL=os.environ['TEL_CHAN']

initQueue()

print("Ready for work.")
worker()
