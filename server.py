#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Setup Python logging --------------------------------------------------------
import logging

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


# Imports----------------------------------------------------------------------
# Load models to communicate with DB. Variable "db" can be accessed anywhere in this file
import pika
from models import *
from common import *


# map = Maps
# s = Maps.get(Maps.owner_id == 5)
# map = Maps(owner_id=5)
# map.save()

# for s in Maps.select().where(Maps.owner_id==5):
#     print s.map_id, s.owner_id

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# "durable" means that queue won't be lost even if RabbitMQ restarts
channel.queue_declare(queue='register_nickname', durable=True)


def on_register_nickname(ch, method, props, body):
    print(" [x] Received %r" % body)
    # Sleep 2 secs

    resp = pack_resp(COMMAND.REGISTER_NICKNAME, RESP.OK)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=resp)
    ch.basic_ack(delivery_tag=method.delivery_tag)



# This tells RabbitMQ not to give more than one message to a worker at a time.
# channel.basic_qos(prefetch_count=1)

channel.basic_consume(on_register_nickname, queue='register_nickname', no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

