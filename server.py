#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Setup Python logging --------------------------------------------------------
# import logging

# FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
# logging.basicConfig(level=logging.DEBUG, format=FORMAT)
# LOG = logging.getLogger()


# Imports----------------------------------------------------------------------
# Load models to communicate with DB. Variable "db" can be accessed anywhere in this file
import pika
from models import *
from common import *


# map = Map
# m = Map.get(Map.owner_id == 3)
# map = Player(nickname="sdasds")
# m = Map(owner_id=3)
# m.save()

# Map.select().where(Map.owner_id==3)

# for s in Map.select().where(Map.owner==3):
#     print s.map_id, s.owner.player_id, s.owner.nickname

# print Player_to_map.select()
#
# for s in Player_hits.select().where(Player_hits.map_id == 8):
#     print s.shot_id, s.map_id, s.player_id, s.player.nickname, s.time

# for s in Invitations.select().where(Invitations.map_id == 8):
#     print s.invitation_id, s.map_id, s.initiator_id, s.invited_player_id

    # print s.shot_id, s.map_id, s.player_id, s.player.nickname, s.time

# print 25
# for s in Map.select().where(Map.owner_id==3):
#     print s.map_id, s.owner_id


def register_nickname(nickname=""):
    '''
    :param nickname: (str)
    :return: (enum) - response code
    '''
    nickname_exists = Player.select().where(Player.nickname == nickname).count()
    resp_code = RESP.NICKNAME_ALREADY_EXISTS

    # If nickname doesn't exist in DB, then create it
    if not nickname_exists:
        Player.create(nickname=nickname)
        resp_code = RESP.OK

    return resp_code


def register_hit(map_id, player_id, row, column):
    '''
    :param map_id: (str)
    :param player_id: (int)
    :param row: (str) x - coordinate where player made a shot
    :param column: (str) y - coordinate where player made a shot
    :return: (enum) - response code, (str) - result of shot (0 - missed, 1 - hit)
    '''
    # map_id, row, column = [int(v) for v in [map_id, row, column]]
    resp_code, hit = RESP.OK, ""

    if Player_hits.select().where(Player_hits.map == map_id,
                                  Player_hits.player == player_id,
                                  Player_hits.row == row,
                                  Player_hits.column == column).count() == 0:

        # TODO: add check if someone stayed in this region, if yes hit = 1, otherwise hit = 0

        hit = 1
        Player_hits.create(map=map_id, player=player_id, row=row, column=column, hit=hit)
    else:
        resp_code = RESP.SHOT_WAS_ALREADY_MADE_HERE

    return resp_code, hit


def create_new_map(owner_id, name, rows, columns):
    '''
    Create a new map with size of (rows x columns)
    :param owner_id: (int)
    :param name: (str) - map name
    :param rows: (str)
    :param columns: (str)
    :return: (enum) - response code, (str) map_id
    '''
    resp_code, map_id = "", ""

    # Check that map with the same name doesn't exist in DB
    if Map.select().where(Map.name == name).count() == 0:
        # Create a new map
        Map.create(owner=owner_id, name=name, rows=rows, columns=columns)
        map_id = Map.select().order_by(Map.map_id.desc()).get().map_id

        resp_code = RESP.OK
    else:
        resp_code = RESP.MAP_NAME_ALREADY_EXISTS

    return resp_code, map_id


nickname = "sdasds"
player_id = Player.get(Player.nickname == nickname).player_id
# map_id, row, column = "9", "3", "5"

# r = register_nickname()
# player = Player.select().where(Player.nickname==seached_nickname).get()
# print player_id

# resp_code, hit_result = register_hit(map_id, player_id, row, column)
resp_code, map_id = create_new_map(player_id, "new map 2.0", "25", "30")
print resp_code, map_id


# Set-up RabbitMQ connection
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

