#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Setup Python logging --------------------------------------------------------
import logging


def start_logger():
    FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    LOG = logging.getLogger()
    return LOG


# Imports----------------------------------------------------------------------
from common import *
import pika  # for Msg Queue
import uuid  # for generating unique correcaltion_id



connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()


# "durable" means that queue won't be lost even if RabbitMQ restarts
channel.queue_declare(queue='register_nickname', durable=True)

# Register the nickname

nickname = "my_nickname"




response = None
corr_id = str(uuid.uuid4())


def on_response(ch, method, props, body):
    if corr_id == props.correlation_id:
        response = body
        print(response)


# create queue for collecting results only for this user
result = channel.queue_declare(exclusive=True)
callback_queue = result.method.queue



channel.basic_publish(exchange='',
                       routing_key='register_nickname',
                       body=nickname,
                       properties=pika.BasicProperties(
                           reply_to=callback_queue,
                           correlation_id=corr_id,
                       ))


channel.basic_consume(on_response, no_ack=True, queue=callback_queue)

connection.process_data_events()
# LOG = start_logger()


# channel.start_consuming()



connection.close()