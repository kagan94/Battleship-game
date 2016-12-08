#! /usr/bin/env python
# =*= coding: utf=8 =*=

# Setup Python logging ==================================================================================
# import logging

# FORMAT = '%(asctime)=15s %(levelname)s %(message)s'
# logging.basicConfig(level=logging.DEBUG, format=FORMAT)
# LOG = logging.getLogger()


# Imports ===============================================================================================
# Load models to communicate with DB. Variable "db" can be accessed anywhere in this file
import pika
from models import *
from common import *



# TODO: delete in final version
# import requests
#
# def rest_queue_list(user='guest', password='guest', host='localhost', port=15672, virtual_host="localhost"):
#     url = 'http://%s:%s/api/queues/%s' % (host, port, virtual_host or '')
#     response = requests.get(url, auth=(user, password))
#     queues = [q['name'] for q in response.json()]
#     return queues

# connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=MQ_HOST))
# channel = connection.channel()
#
# for queue_name in rest_queue_list():
#     channel.queue_delete(queue=queue_name)
#
# connection.close()


def refresh_db_connection(f):
    ''' It's a decorator to refresh DB connection '''
    def tmp(*args, **kwargs):
        # It's fix to avoid error "MySQL was gone away".
        # Here we check whether our current db connection is accessible or not (if not, refresh it)
        db.get_conn().ping(True)

        return f(*args, **kwargs)
    return tmp


def send_response(reply_queue, query):
    '''
    This function put query into the specified queue
    :param reply_queue: (str) queue - where to place query
    :param query: (str) - compressed query
    '''
    print "response sent: %s" % query

    channel.basic_publish(exchange='',
                          routing_key=reply_queue,
                          body=query,
                          properties=pika.BasicProperties(
                              delivery_mode=2
                          ))


# Handlers for queue ===================================================================================
def on_register_nickname(ch, method, props, body):
    print(" [x] Received reg nick %r" % body)

    command, nickname = parse_query(body)

    resp_code = register_nickname(nickname)
    response = pack_resp(COMMAND.REGISTER_NICKNAME, resp_code, nickname)

    print "Resp_code: %s" % resp_code

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     body=response,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id)
                     )

    ch.basic_ack(delivery_tag=method.delivery_tag)


def on_user_request(ch, method, props, body):
    print(" [x] Received %r" % body)

    query = None

    nickname = method.routing_key[len("req_"):]
    player_id = player_id_by_nickname(nickname)

    command, data = parse_query(body)

    if command == COMMAND.CREATE_NEW_GAME:

        resp_code, map_id = create_new_map(owner_id=player_id, name=data, rows='5', columns='5')

        query = pack_resp(command, resp_code, data=map_id)

    elif command == COMMAND.JOIN_EXISTING_GAME:
        pass

    elif command == COMMAND.PLACE_SHIP:
        pass

    elif command == COMMAND.MAKE_HIT:
        pass

    elif command == COMMAND.DISCONNECT_FROM_GAME:
        pass

    elif command == COMMAND.QUIT_FROM_GAME:
        pass

    elif command == COMMAND.START_GAME:
        pass

    elif command == COMMAND.RESTART_GAME:
        pass

    elif command == COMMAND.INVITE_PLAYERS:
        pass

    # Put response into the queue
    if query:
        reply_queue = "resp_" + nickname

        send_response(reply_queue=reply_queue, query=query)

    # Remove read msg rom queue
    channel.basic_ack(delivery_tag=method.delivery_tag)


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


# Main functions =====================================================================================
@refresh_db_connection
def player_id_by_nickname(nickname):
    return Player.get(Player.nickname == nickname).player_id


@refresh_db_connection
def register_nickname(nickname=""):
    '''
    :param nickname: (str)
    :return: (enum) = response code
    '''


    nickname_exists = Player.select().where(Player.nickname == nickname).count()
    resp_code = RESP.NICKNAME_ALREADY_EXISTS

    # If nickname doesn't exist in DB, then create it
    if not nickname_exists:
        Player.create(nickname=nickname)
        print "created nick" + nickname

        resp_code = RESP.OK

        # Register new queue with user name
        req_nickname_queue = "req_" + nickname
        resp_nickname_queue = "resp_" + nickname

        channel.queue_declare(queue=req_nickname_queue, durable=True)
        channel.queue_declare(queue=resp_nickname_queue, durable=True)

        # print "req_nickname_queue: %s" % req_nickname_queue
        channel.basic_consume(on_user_request, queue=req_nickname_queue)

    return resp_code


@refresh_db_connection
def register_hit(map_id, player_id, row, column):
    '''
    :param map_id: (str)
    :param player_id: (int)
    :param row: (str) x = coordinate where player made a shot
    :param column: (str) y = coordinate where player made a shot
    :return: (enum) = response code, (str) = result of shot (0 = missed, 1 = hit)
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


@refresh_db_connection
def create_new_map(owner_id, name, rows, columns):
    '''
    Create a new map with size of (rows x columns)
    :param owner_id: (int)
    :param name: (str) = map name
    :param rows: (str)
    :param columns: (str)
    :return: (enum) = response code, (str) map_id
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

    return resp_code, str(map_id)


# nickname = "sdasds"
# player_id = Player.get(Player.nickname == nickname).player_id
# map_id, row, column = "9", "3", "5"

# r = register_nickname()
# player = Player.select().where(Player.nickname==seached_nickname).get()
# print player_id

# resp_code, hit_result = register_hit(map_id, player_id, row, column)
# resp_code, map_id = create_new_map(player_id, "new map 2.0", "25", "30")

# print resp_code, map_id


# Set=up RabbitMQ connection



@refresh_db_connection
def attach_handler_for_existing_players():
    ''' Attach handler for existing users, to fetch new requests in the queue '''
    print 1
    for player in Player.select():
        queue_name = 'req_' + player.nickname
        # print "queue_name: %s" % queue_name

        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_consume(on_user_request, queue=queue_name)




# This tells RabbitMQ not to give more than one message to a worker at a time.
# channel.basic_qos(prefetch_count=1)

connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=MQ_HOST))
channel = connection.channel()

# "durable" means that queue won't be lost even if RabbitMQ restarts
channel.queue_declare(queue='register_nickname', durable=True)

# Attach triggers to queues
channel.basic_consume(on_register_nickname, queue='register_nickname')
attach_handler_for_existing_players()

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

connection.close()

