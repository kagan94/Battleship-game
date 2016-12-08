#!/usr/bin/env python

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()


# "durable" means that queue won't be lost even if RabbitMQ restarts
channel.queue_declare(queue='my_queue', durable=True)

msg = "Hello World!"
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=msg,
                      properties=pika.BasicProperties(
                          delivery_mode=2,  # mark message as persistent
                      ))

print(" [x] Sent 'Hello World!'")

connection.close()

