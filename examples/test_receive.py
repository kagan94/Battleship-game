#!/usr/bin/env python

import pika, time

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()


# "durable" means that queue won't be lost even if RabbitMQ restarts
channel.queue_declare(queue='my_queue', durable=True)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    # Sleep 2 secs
    time.sleep(2)

    ch.basic_ack(delivery_tag=method.delivery_tag)


# This tells RabbitMQ not to give more than one message to a worker at a time.
channel.basic_qos(prefetch_count=1)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()


