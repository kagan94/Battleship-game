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
import peewee

# Local files
from models import *
from common import *
from ship_placement import *

from argparse import ArgumentParser  # Parsing command line arguments
from redis import ConnectionPool, Redis  # Redis middleware


# TODO: delete in final version
def DELETE_ALL_QUEUES():
    import requests

    def rest_queue_list(user='guest', password='guest',
                        host=RABBITMQ_HOST, port=15672, virtual_host=RABBITMQ_VIRTUAL_HOST):
        url = 'http://%s:%s/api/queues/%s' % (host, port, virtual_host or '')
        response = requests.get(url, auth=(user, password))
        queues = [q['name'] for q in response.json()]
        return queues

    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST,
                                  virtual_host=RABBITMQ_VIRTUAL_HOST,
                                  credentials=credentials))
    channel = connection.channel()

    for queue_name in rest_queue_list():
        channel.queue_delete(queue=queue_name)

    connection.close()
    print "All queues were deleted"

# DELETE_ALL_QUEUES()


def check_db_connection():
    ''' Check connect with MySQL dababase. If is not return False '''
    db_connection = True
    try:
        db.get_conn().ping(True)
    except peewee.OperationalError:
        print "ERROR: Problem with DB connection"
        db_connection = False
    return db_connection


def refresh_db_connection(f):
    ''' It's a decorator to refresh DB connection '''

    def tmp(*args, **kwargs):
        # It's fix to avoid error "MySQL was gone away".
        # Here we check whether our current db connection is accessible or not (if not, refresh it)
        return f(*args, **kwargs) if check_db_connection() else None
    return tmp


class Main_Server(object):
    def __init__(self, server_name):
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

        self.redis_conn = None

        self.server_name = server_name
        self.server_id = None

    def server_online(self):
        '''
            Put msg into queue "servers_online" to notify about server presence
        '''

        server = Server.select().where(Server.name == self.server_name)

        # Server already registered in DB, fetch its id
        if server.count() > 0:
            print "- Fetch existing server_id from DB (by server name)"
            self.server_id = str(server.get().server_id)

        # Register server in DB
        else:
            print "- Save new server name in DB"
            Server.create(name=self.server_name)
            self.server_id = self.server_id_by_name(self.server_name)

        print "<< Server(%s) sent server_name to Redis about its presence" % self.server_name

        # Add server name to the hash set "servers_online" in Redis
        # (in format key:value)
        if not self.redis_conn.hexists("servers_online", self.server_id):
            self.redis_conn.hset("servers_online", self.server_id, self.server_name)

    def server_offline(self):
        '''
            Remove msg from the set "servers_online". It means server off-line
        '''

        # Server goes off-line (remove server name from the set "servers_online")
        if not self.redis_conn.hexists("servers_online", self.server_id):
            self.redis_conn.hdel("servers_online", self.server_id)

    def open_rabbitmq_connection(self, host, login, password, virtual_host):
        #############
        # Set up RabbitMQ connection
        #############

        try:
            print "- Start establishing connection to RabbitMQ server."

            credentials = pika.PlainCredentials(login, password)
            self.rabbitmq_connection = pika.BlockingConnection(
                            pika.ConnectionParameters(host=host,
                                                      virtual_host=virtual_host,
                                                      credentials=credentials))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()

            print "- Connection to RabbitMQ server is established."

            # "durable" means that queue won't be lost even if RabbitMQ restarts
            self.rabbitmq_channel.queue_declare(queue='register_nickname', durable=True)

            # Attach triggers to queues
            self.rabbitmq_channel.basic_consume(self.on_register_nickname, queue='register_nickname')
            self.attach_handler_to_existing_players()

        except:
            print "ERROR: Can't access RabbitMQ server, please check connection parameters."
            self.rabbitmq_connection = None

    def open_redis_connection(self, host, port):
        #############
        # Set up Redis connection
        #############

        print "- Start establishing connection to Redis server."

        pool = ConnectionPool(host=host, port=port, db=0)
        self.redis_conn = Redis(connection_pool=pool)

        # Check that Redis server is accessible
        # If not, set redis connection to None
        if not check_redis_connection(self.redis_conn):
            self.redis_conn = None
        else:
            print "- Connection to Redis server is established."

    def start_consuming(self):
        print('[*] Waiting for messages. To exit press CTRL+C')

        try:
            self.rabbitmq_channel.start_consuming()

        except SystemExit, KeyboardInterrupt:
            self.rabbitmq_connection.close()

            # Mark server off-line (in Redis)
            self.server_offline()

    def send_response(self, nickname, query):
        '''
        This function put query into the specified queue

        :param nickname: (str) - needs to put query into correct queue for particular nickname (player)
        :param query: (str) - compressed query
        '''
        print "<< Response sent: %s" % query

        reply_queue = "resp_" + nickname

        self.rabbitmq_channel.basic_publish(exchange='',
                                            routing_key=reply_queue,
                                            body=query,
                                            properties=pika.BasicProperties(
                                                delivery_mode=2
                                            ))

    @refresh_db_connection
    def attach_handler_to_existing_players(self):
        '''
            Attach handler for existing users, to fetch new requests in the queue
        '''
        for player in Player.select():
            queue_name = 'req_' + player.nickname

            self.rabbitmq_channel.queue_declare(queue=queue_name, durable=True)
            self.rabbitmq_channel.basic_consume(self.on_user_request, queue=queue_name)

            # Create queue to put responses for particular user
            self.rabbitmq_channel.queue_declare(queue='resp_' + player.nickname, durable=True)

###################
    # Main functions =====================================================================================
    ###################
    @refresh_db_connection
    def server_id_by_name(self, server_name):
        return Server.get(Server.name == server_name).server_id

    @refresh_db_connection
    def player_id_by_nickname(self, nickname):
        return Player.get(Player.nickname == nickname).player_id

    @refresh_db_connection
    def map_exists(self, map_id):
        return Map.select().where(Map.map_id == map_id,
                                  Map.server == self.server_id).count() > 0

    @refresh_db_connection
    def register_nickname(self, nickname=""):
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

            self.rabbitmq_channel.queue_declare(queue=req_nickname_queue, durable=True)
            self.rabbitmq_channel.queue_declare(queue=resp_nickname_queue, durable=True)

            # print "req_nickname_queue: %s" % req_nickname_queue
            self.rabbitmq_channel.basic_consume(self.on_user_request, queue=req_nickname_queue)

        return resp_code

    @refresh_db_connection
    def make_hit(self, map_id, player_id, row, column):
        '''
        :param map_id: (str)
        :param player_id: (int)
        :param row: (str) x = coordinate where player made a shot
        :param column: (str) y = coordinate where player made a shot
        :return: (enum) = response code, (str) = result of shot (0 = missed, 1 = hit)
        '''
        # map_id, row, column = [int(v) for v in [map_id, row, column]]
        # is_game_end can be "0" or "1"
        resp_code, hit, is_game_end = RESP.OK, "", "0"

        # Map doesn't exist
        if not self.map_exists(map_id):
            resp_code = RESP.MAP_DOES_NOT_EXIST

        # Player already made shot in this region
        elif Player_hits.select().where(Player_hits.map == map_id,
                                        Player_hits.player == player_id,
                                        Player_hits.row == row,
                                        Player_hits.column == column).count() > 0:
            resp_code = RESP.SHOT_WAS_ALREADY_MADE_HERE

        # Register new shot
        else:
            hit = "1"

            Player_hits.create(map=map_id, player=player_id, row=row, column=column, hit=hit)

            # TODO: add check if someone stayed in this region, if yes hit = 1, otherwise hit = 0

            # TODO: if shot was successful, check is the game ended and change var "is_game_end"
            is_game_end = "1"  # ?????? change later

            # TODO: Check whether ship is completely sank, then send argument "completely_sank" to player who made shot

            # TODO: if ship sank, send notification to damaged player
            # TODO: notify next player if hit = 0

        return resp_code, hit, is_game_end

    @refresh_db_connection
    def create_new_map(self, owner_id, name, rows, columns):
        '''
        Create a new map with size of (rows x columns)

        :param owner_id: (int)
        :param name: (str) = map name
        :param rows: (str)
        :param columns: (str)
        :return: (enum) = response code, (str) map_id
        '''
        resp_code, map_id = RESP.OK, ""

        # Check that map with the same name doesn't exist in DB
        if Map.select().where(Map.name == name,
                              Map.server == self.server_id).count() == 0:
            # Create a new map
            Map.create(owner=owner_id, server=self.server_id, name=name, rows=rows, columns=columns)
            map_id = Map.select().order_by(Map.map_id.desc()).get().map_id

        else:
            resp_code = RESP.MAP_NAME_ALREADY_EXISTS

        return resp_code, str(map_id)

    @refresh_db_connection
    def join_game(self, map_id, player_id, player_nickname):
        '''
        Player wants to join existing game

        :param map_id: (str) - map that user wants to join
        :param player_id: (str)
        :param player_nickname: (str)
        :return: resp_code (enum)
        '''
        resp_code = RESP.OK

        # Map doesn't exist
        if not self.map_exists(map_id):
            resp_code = RESP.MAP_DOES_NOT_EXIST

        # Game session already started on requested map
        elif Map.select().where(Map.map_id == map_id,
                                Map.server == self.server_id,
                                Map.game_started == 1).count() > 0:
            resp_code = RESP.GAME_ALREADY_STARTED

        # Player already joined this map
        elif Player_to_map.select().where(Player_to_map.map == map_id,
                                          Player_to_map.player == player_id).count() > 0:
            resp_code = RESP.OK
            # resp_code = RESP.ALREADY_JOINED_TO_MAP

        # Add player to the requested map
        else:
            Player_to_map.create(map_id=map_id, player=player_id)

            try:
                map_creator = Map.select().where(Map.map_id == map_id,
                                                 Map.server == self.server_id).get()

                # Check that current player and creator of the map are different players
                if map_creator.owner.player_id != player_id:
                    # Notify admin about joining a new player
                    query = pack_resp(COMMAND.NOTIFICATION.PLAYER_JOINED_TO_GAME, RESP.OK, player_nickname)
                    self.send_response(map_creator.owner.nickname, query)

            except Map.DoesNotExist:
                pass

        return resp_code

    @refresh_db_connection
    def list_of_maps(self):
        '''
        :return: (data) - packed data in format (map_id, map_name, rows, columns)
        '''
        data = ""
        maps_data = []

        # Get all games which have not been started yet
        maps_query = Map.select().where(Map.server == self.server_id,
                                        Map.game_started == 0)

        for m in maps_query:
            # Compress data
            map_data = (m.map_id, m.name, m.rows, m.columns)
            for el in zip(map_data):
                maps_data.append(str(el[0]))

        data = pack_data(maps_data)
        return RESP.OK, data

    ###################
    # Handlers for queue ===================================================================================
    ###################
    def on_register_nickname(self, ch, method, props, body):
        print(">> Received command to register nickname: %s" % body)

        command, server_id, nickname = parse_query(body)

        resp_code = self.register_nickname(nickname)
        response = pack_resp(COMMAND.REGISTER_NICKNAME, resp_code, data=nickname)

        print "Resp_code: %s" % resp_code

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         body=response)

        # Remove msg after reading
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def on_user_request(self, ch, method, props, body):
        '''
        It's main handler to process players requests

        :param ch: channel
        :param method: -
        :param props: -
        :param body: message
        '''

        query = None

        nickname = method.routing_key[len("req_"):]
        player_id = self.player_id_by_nickname(nickname)

        command, server_id, data = parse_query(body)

        print ">> Received command: %s, data: %s" % (command_to_str(command), data)

        # +
        if command == COMMAND.LIST_OF_MAPS:
            resp_code, data = self.list_of_maps()
            query = pack_resp(command, resp_code, self.server_id, data)

        # +
        elif command == COMMAND.CREATE_NEW_GAME:
            resp_code, map_id = self.create_new_map(owner_id=player_id, name=data,
                                                    rows='5', columns='5')
            query = pack_resp(command, resp_code, self.server_id, data=map_id)

        # +
        elif command == COMMAND.JOIN_EXISTING_GAME:
            resp_code = self.join_game(map_id=data, player_id=player_id, player_nickname=nickname)
            query = pack_resp(command, resp_code, self.server_id)

        # +
        elif command == COMMAND.PLACE_SHIPS:
            resp_code, data = place_ships(map_id=data, player_id=player_id)
            query = pack_resp(command, resp_code, self.server_id, data)

        # +
        elif command == COMMAND.MAKE_HIT:
            map_id, row, column = parse_data(data)

            resp_code, hit, is_game_end = self.make_hit(map_id, player_id, row, column)
            data = pack_data([hit, is_game_end])

            query = pack_resp(command, resp_code, self.server_id, data)

        elif command == COMMAND.DISCONNECT_FROM_GAME:
            pass

        elif command == COMMAND.QUIT_FROM_GAME:
            pass

        elif command == COMMAND.START_GAME:
            pass

        elif command == COMMAND.RESTART_GAME:
            pass

        elif command == COMMAND.KICK_PLAYER:
            pass

        # Put response into the queue
        if query:
            self.send_response(nickname=nickname, query=query)

        # Remove read msg rom queue
        self.rabbitmq_channel.basic_ack(delivery_tag=method.delivery_tag)

# nickname = "sdasds"
# player_id = Player.get(Player.nickname == nickname).player_id
# map_id, row, column = "9", "3", "5"

# r = register_nickname()
# player = Player.select().where(Player.nickname==seached_nickname).get()
# print player_id

# resp_code, hit_result = register_hit(map_id, player_id, row, column)
# resp_code, map_id = create_new_map(player_id, "new map 2.0", "25", "30")

# print resp_code, map_id

# ================================
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


###################
# Main function to parse args and run server
###################
def main():
    # Parsing arguments
    parser = ArgumentParser()
    parser.add_argument('-n', '--server_name',
                        help='Enter server name')

    # Args for RabbitMQ
    parser.add_argument('-rmqh','--rabbitmq_host',
                        help='Host for RabbitMQ connection, default is %s' % RABBITMQ_HOST,
                        default=RABBITMQ_HOST)
    parser.add_argument('-rmqcr','--rabbitmq_credentials',
                        help='Credentials for RabbitMQ connection in format "login:password",'
                             'default is %s' % RABBITMQ_CREDENTIALS,
                        default=RABBITMQ_CREDENTIALS)
    parser.add_argument('-rmqvh','--rabbitmq_virtual_host',
                        help='Virtual host for RabbitMQ connection, default is "%s"' % RABBITMQ_VIRTUAL_HOST,
                        default=RABBITMQ_VIRTUAL_HOST)

    # Args for Redis
    parser.add_argument('-rh', '--redis_host',
                        help='Host for Redis connection, default is %s' % REDIS_HOST,
                        default=REDIS_HOST)
    parser.add_argument('-rp', '--redis_port', type=int,
                        help='Port for Redis connection, default is %d' % REDIS_PORT,
                        default=REDIS_PORT)

    args = parser.parse_args()
    server_name = args.server_name

    # except KeyboardInterrupt:
    #     print "Terminating by keyboard interrupt..."

    if server_name is None:
        print "Please, specify server name."
        parser.print_help()

    # Can't access MySQL server
    elif not check_db_connection():
        return

    # Run server
    else:
        server = Main_Server(server_name)

        server.open_redis_connection(args.redis_host, args.redis_port)

        login, password = args.rabbitmq_credentials.split(":")
        server.open_rabbitmq_connection(args.rabbitmq_host, login, password, args.rabbitmq_virtual_host)

        # If connections to RabbitMQ and Rebis were established successfully, run server
        if server.rabbitmq_connection and server.redis_conn:
            print "####################"

            try:
                # Mark server on-line (in Redis)
                server.server_online()

                # Start receiving queries
                server.start_consuming()

            except (KeyboardInterrupt, SystemExit):
                print 'Terminating ...'

                server.rabbitmq_connection.close()

                # Show clients that server is not online anymore (in Redis)
                # Mark server off-line (in Redis)
                server.server_offline()


if __name__ == "__main__":
    main()
