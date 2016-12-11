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
import pika  # for Msg Queue
import uuid  # for generating unique correcaltion_id
import ConfigParser as CP
from threading import Thread
from argparse import ArgumentParser  # Parsing command line arguments
from redis import ConnectionPool, Redis  # Redis middleware

# Local files
from gui import *
from common import *

# Path to the config file
current_path = os.path.abspath(os.path.dirname(__file__))
config_file = os.path.join(current_path, "config.ini")


class Client(object):
    gui = None
    connection = None
    channel = None

    nickname = None

    temp_queue, temp_queue_name = None, ""
    chosen_server_id = None

    def __init__(self):
        self.nickname = None

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

        except:
            print "ERROR: Can't access RabbitMQ server, please check connection parameters."
            self.rabbitmq_connection = None

    def close_rabbitmq_connection(self):
        self.rabbitmq_connection.close()

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

    def send_request(self, query):
        '''
            Put request into the client queue for server
            Later server will fetch this query

            :param query: (str) packed command, data in one string
        '''

        print "<< Query (%s) put into request queue" % query

        request_queue = 'req_' + self.nickname
        self.rabbitmq_channel.basic_publish(exchange='',
                                            routing_key=request_queue,
                                            body=query)

    def check_nickname(self):
        '''
        :return: (str) if nickname exists locally, return it. Otherwise False.
        '''

        # If the config exists, get the user_id from it
        if os.path.isfile(config_file):
            print "Nickname exists locally"

            conf = CP.ConfigParser()
            conf.read(config_file)

            self.nickname = conf.get('USER_INFO', 'nickname')

            # Run servers_online window
            self.gui.choose_server_window()

        # Nickname wasn't found in local config
        else:
            # Create temp queue to collect the response from "register_nickname" operation
            if not self.temp_queue:
                self.temp_queue = self.rabbitmq_channel.queue_declare()
                self.temp_queue_name = self.temp_queue.method.queue

            # Bind some triggers to queues
            self.rabbitmq_channel.basic_consume(self.on_response, queue=self.temp_queue_name)

            # TODO: Launch GUI window to enter nickname (Ask player to enter his nickname)
            self.gui.nickname_window()

    def register_nickname(self, nickname):
        '''
        Register the nickname provided by player

        :param nickname: (str)
        '''
        # nickname = "my_nicknam1234" + str(uuid.uuid4())

        command = COMMAND.REGISTER_NICKNAME
        query = pack_query(command, data=nickname)

        self.rabbitmq_channel.basic_publish(exchange='',
                                            routing_key='register_nickname',
                                            body=query,
                                            properties=pika.BasicProperties(
                                                reply_to=self.temp_queue_name,
                                                delivery_mode=2
                                            ))

        print "Try to register nickname"
        while self.nickname is None:
            self.rabbitmq_connection.process_data_events()

        # resp_code, hit = register_hit(map_id, player_id, row, column)

        # TODO: Block the window

    # Main methods for GUI ============================================================
    def create_new_game(self, game_name):
        '''
        Register a new game on the server

        :param game_name: (str)
        '''

        # Put query into MQ to register a new game
        query = pack_query(COMMAND.CREATE_NEW_GAME, self.chosen_server_id, data=game_name)
        self.send_request(query)

    def join_game(self, map_id):
        '''
        Register a new game on the server

        :param map_id: (str) - map that player wants to connect
        '''

        # Put query into MQ to join existing game
        query = pack_query(COMMAND.JOIN_EXISTING_GAME, self.chosen_server_id, map_id)
        self.send_request(query)

    def place_ships(self, map_id):
        ''' Place ships randomly '''
        query = pack_query(COMMAND.PLACE_SHIPS, self.chosen_server_id, data=map_id)
        self.send_request(query)

    def register_hit(self, map_id, target_row, target_column):
        '''
        Register a new hit on the map

        :param map_id: (str)
        :param target_row: (str)
        :param target_column: (str)
        '''

        data = pack_data([map_id, target_row, target_column])
        query = pack_query(COMMAND.MAKE_HIT, self.chosen_server_id, data)

        # Put query to register a new hit
        self.send_request(query)

    def available_servers(self):
        '''
        :return: (list) of serves in state on-line
        '''
        servers = []

        # Request to get server online from Redis
        # Set of servers online
        servers_online = self.redis_conn.smembers("servers_online")

        if servers_online:
            # Convert set of servers to list
            servers = sorted(list(servers_online))
            servers.sort()

            print "Servers online: " + ", ".join(servers)
        else:
            print "All server are off-line"

        return servers

    # Handlers ========================================================================
    def on_response(self, channel, method, props, body):
        # if props.correlation_id in self.corr_ids.keys():

        # Delete received response on requested command
        # command = self.corr_ids[props.correlation_id]
        # del self.corr_ids[props.correlation_id]

        # print body
        command, resp_code, server_id, data = parse_response(body)

        # print command, resp_code, server_id, data

        print ">> Received resp(%s) on command: %s, server(%s)"\
              % (error_code_to_string(resp_code), command_to_str(command), server_id)

        if command == COMMAND.REGISTER_NICKNAME:
            ''' Handler to receive response on request reg_me '''
            command, resp_code, server_id, data = parse_response(body)

            if resp_code == RESP.OK:
                print "Nickname was registered successfully"

                self.nickname = data

                # Save nickname in local config
                conf = CP.RawConfigParser()
                conf.add_section("USER_INFO")
                conf.set('USER_INFO', 'nickname', self.nickname)

                with open(config_file, 'w') as cf:
                    conf.write(cf)

                # Delete temporary queue if exists
                if self.temp_queue:
                    self.rabbitmq_channel.queue_delete(queue=self.temp_queue_name)

                self.gui.choose_server_window()

            else:
                # Unfreeze blocked submit button in GUI
                self.gui.check_nick_button.config(state=NORMAL)
                print "Register nickname error: %s" % error_code_to_string(resp_code)

        # +
        elif command == COMMAND.CREATE_NEW_GAME:
            map_id = data

            if resp_code == RESP.OK:
                pass
                # TODO: Update GUI, open new field
            else:
                pass
                # TODO: Update notification area

        # +
        elif command == COMMAND.JOIN_EXISTING_GAME:
            if resp_code == RESP.OK:
                pass
                # TODO: Update GUI, open the field with existing game
            else:
                # TODO: Update notification area - show errors
                pass

        # +
        elif command == COMMAND.PLACE_SHIPS:
            if resp_code == RESP.OK:
                info = parse_data(data)
                ships_locations = []

                # Parse (x1, x2, y1, y2, and ship size) as tuple
                for i in range(0, len(info), 5):
                    ship = (info[i], info[i + 1], info[i + 2], info[i + 3], info[i + 4])
                    ships_locations.append(ship)

                # ships_locations = [(x1, x2, y1, y2, ship_size), ...]
                print ships_locations

            else:
                print error_code_to_string(resp_code)
                # TODO: Update notification area

        # +
        elif command == COMMAND.MAKE_HIT:
            if resp_code == RESP.OK:
                hit, is_game_end = parse_data(data)

                # TODO: Update GUI. Add hit to the map.
                # TODO: If game end, then block field + update notification area

                # TODO: Check whether ship is completely sank
            else:
                pass
                # TODO: Update notification

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

        # NOTIFICATIONS FROM SERVER
        # 1) If I'm owner of the map and another player joined
        # 2) Another player damaged my ship
        # 3) My ship sank
        # 4) My turn to move
        # 5) You're kicked
        # 6) Another player damaged another player's ship

        # +
        elif command == COMMAND.NOTIFICATION.PLAYER_JOINED_TO_GAME:
            joined_player = data  # nickname
            # (!) Don't need to check resp_code

            # TODO: GUI update status bar about joined player

        elif command == COMMAND.NOTIFICATION.YOUR_SHIP_WAS_DAMAGED:

            # TODO: Check whether ship is completely sank
            pass

        elif command == COMMAND.NOTIFICATION.YOUR_TURN_TO_MOVE:
            pass

        elif command == COMMAND.NOTIFICATION.YOU_ARE_KICKED:
            pass

        # ????? Do we really need it????????????????????????????????????
        elif command == COMMAND.NOTIFICATION.SOMEONES_SHIP_SANK:
            pass

        # Remove read msg rom queue
        channel.basic_ack(delivery_tag=method.delivery_tag)

    #############
    # Main loop for receiving notifications
    #############
    def notifications_loop(self, host, login, password, virtual_host):
        ''' Open new RabbitMQ connection to receive notifications '''
        if 1:
        # try:
            print "- Start establishing connection to RabbitMQ server."

            credentials = pika.PlainCredentials(login, password)
            connection = pika.BlockingConnection(
                            pika.ConnectionParameters(host=host,
                                                      virtual_host=virtual_host,
                                                      credentials=credentials))
            channel = connection.channel()
            print "- Connection to RabbitMQ server is established."

            # Bind trigger to response queue
            resp_queue = "resp_" + self.nickname

            channel.queue_declare(queue=resp_queue, durable=True)
            channel.basic_consume(self.on_response, queue=resp_queue)

            channel.start_consuming()

            # Close MQ connection if still opened
            if not connection.is_closed:
                connection.close()

        # except:
        #     print "ERROR: Can't access RabbitMQ server, please check connection parameters."


def main():
    # Parsing arguments
    parser = ArgumentParser()

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

    # Before Client starts working, we need to check connections to RabbitMQ and Redis
    client = Client()
    gui = GUI()

    # Client can trigger GUI and vice-versa (at anytime)
    client.gui = gui
    gui.client = client

    # Open connection to Redis server
    client.open_redis_connection(args.redis_host, args.redis_port)

    # Open connection to RabbitMQ server
    login, password = args.rabbitmq_credentials.split(":")
    client.open_rabbitmq_connection(args.rabbitmq_host, login, password, args.rabbitmq_virtual_host)

    # If connections to RabbitMQ and Rebis were established successfully, run Client
    if client.rabbitmq_connection and client.redis_conn:
        print "####################"

        client.check_nickname()

        # TODO: In GUI. Add list of available servers which player can choose
        # print client.available_servers()

        # We connected to chosen server
        client.chosen_server_id = '1'

        if client.nickname and client.chosen_server_id:
            # Declare queue to put requests
            request_queue = 'req_' + client.nickname
            client.rabbitmq_channel.queue_declare(queue=request_queue, durable=True)

            # client.create_new_game("abc game")
            # client.register_hit(map_id='74', target_row='2', target_column='2')
            # client.join_game(map_id='74')
            # client.place_ships(map_id='74')

            # Start notification loop
            notifications_thread = Thread(name='NotificationsThread',
                                          target=client.notifications_loop,
                                          args=(args.rabbitmq_host, login, password, args.rabbitmq_virtual_host,))
            notifications_thread.start()

            # Blocks until the thread finished the work.
            notifications_thread.join()


    # Create 2 separate threads for asynchronous notifications and for main app
    # main_app_thread = Thread(name='MainApplicationThread', target=client.main_app_loop)
    # notifications_thread = Thread(name='NotificationsThread', target=client.notifications_loop)
    #
    # # main_app_thread.start()
    # notifications_thread.start()
    #
    #
    # # !!!! channel.basic_consume(on_register_nickname, queue=resp_nickname_queue)
    # # client.register_nickname("dsa")
    #
    # # gui = GUI(root, client)
    # # client.gui = gui
    #
    # # Blocks until the thread finished the work.
    # notifications_thread.join()
    # main_app_thread.join()

    # client.close_rabbitmq_connection()

    print 'Terminating ...'


if __name__ == "__main__":
    main()
