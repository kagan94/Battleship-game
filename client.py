#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Imports----------------------------------------------------------------------
import pika  # for RabbitMQ Queue

import ConfigParser as CP
from threading import Thread, Lock
from argparse import ArgumentParser  # Parsing command line arguments
from redis import ConnectionPool, Redis  # Redis middleware

# Local files
from gui import *
from common import *

lock = Lock()

# Path to the config file
current_path = os.path.abspath(os.path.dirname(__file__))
config_file = os.path.join(current_path, "config.ini")


class Client(object):
    def __init__(self):
        self.nickname = None
        self.gui = None

        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.rabbitmq = {}  # To store general setting for RabbitMQ such as host, credentials..

        self.temp_queue, temp_queue_name = None, ""

        self.selected_server_id = None

        self.resp = None  # response is empty by default

    def open_rabbitmq_connection(self):
        #############
        # Set up RabbitMQ connection
        #############

        host, virtual_host = self.rabbitmq["host"], self.rabbitmq["virtual_host"]
        login, password = self.rabbitmq["login"], self.rabbitmq["password"]

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
        try:
            self.rabbitmq_connection.close()
        except pika.exceptions.ConnectionClosed:
            pass

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

    def send_request(self, query, after_reconnect=False):
        '''
        Put request into the client queue for server
        Later server will fetch this query
        :param query: (str) packed command, data in one string
        :param after_reconnect: (bool) in case of after reconnecting
        '''

        print "<< Query (%s) put into request queue" % query

        request_queue = 'req_' + self.nickname

        try:
            self.rabbitmq_channel.basic_publish(exchange='',
                                                routing_key=request_queue,
                                                body=query)
        except pika.exceptions.ConnectionClosed:
            if not after_reconnect:
                self.open_rabbitmq_connection()
                self.send_request(query, after_reconnect=True)

                print "Pika connection closed, but now try to reconnect.."

            else:
                print "Pika couldn't reconnect.."


    def save_nickname_locally(self, nickname):
        ''' Save nickname in local config file '''
        self.nickname = nickname

        conf = CP.RawConfigParser()
        conf.add_section("USER_INFO")
        conf.set('USER_INFO', 'nickname', self.nickname)

        with open(config_file, 'w') as cf:
            conf.write(cf)

        # Delete temporary queue if exists
        if self.temp_queue:
            self.rabbitmq_channel.queue_delete(queue=self.temp_queue_name)

    # Main methods for GUI ============================================================
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

        # Nickname wasn't found in local config
        else:
            # Create temp queue to collect the response from "register_nickname" operation
            if not self.temp_queue:
                self.temp_queue = self.rabbitmq_channel.queue_declare()
                self.temp_queue_name = self.temp_queue.method.queue

            # Bind some triggers to queues
            self.rabbitmq_channel.basic_consume(self.on_register_nickname_response, queue=self.temp_queue_name)

    ###########
    # Example of RPC pattern
    ###########
    def register_nickname(self, nickname):
        '''
        Register the nickname provided by player
        :param nickname: (str)
        '''

        command = COMMAND.REGISTER_NICKNAME
        query = pack_query(command, data=nickname)

        self.rabbitmq_channel.basic_publish(exchange='',
                                            routing_key='register_nickname',
                                            body=query,
                                            properties=pika.BasicProperties(
                                                reply_to=self.temp_queue_name,
                                                delivery_mode=2
                                            ))
        print "Try to register nickname..."

        while self.resp is None:
            self.rabbitmq_connection.process_data_events()

        self.resp = None

    def on_register_nickname_response(self, channel, method, props, body):
        self.resp = True
        _, resp_code, _, nickname = parse_response(body)

        if resp_code == RESP.OK:
            self.gui.add_notification("Nickname was registered successfully")

            self.save_nickname_locally(nickname)
            self.gui.choose_server_window()
        else:
            # Unfreeze blocked submit button in GUI
            self.gui.check_nick_button.config(state=NORMAL)

            error_msg = error_code_to_string(resp_code)
            self.gui.add_notification(error_msg)

    def create_new_game(self, game_name, field_size):
        '''
        Register a new game on the server
        :param game_name: (str)
        :param field_size: (int) desired field size for map that shoule be created
            (map will have size field_size * field_size)
        '''

        # Put query into MQ to register a new game
        data = pack_data([game_name, str(field_size)])
        query = pack_query(COMMAND.CREATE_NEW_GAME, self.selected_server_id, data)
        self.send_request(query)

    def join_game(self):
        ''' Join to existing game on a server '''

        # map that player wants to connect
        map_id = self.gui.selected_map_id

        # Put query into MQ to join existing game
        query = pack_query(COMMAND.JOIN_EXISTING_GAME, self.selected_server_id, map_id)
        self.send_request(query)

    def place_ships(self):
        ''' Place ships randomly '''

        query = pack_query(COMMAND.PLACE_SHIPS, self.selected_server_id, data=self.gui.selected_map_id)
        self.send_request(query)

    def make_shot(self, target_row, target_column):
        '''
        Register a new hit on the map
        :param map_id: (str)
        :param target_row: (str)
        :param target_column: (str)
        '''

        data = pack_data([self.gui.selected_map_id, target_row, target_column])
        query = pack_query(COMMAND.MAKE_HIT, self.selected_server_id, data)

        # Put query to register a new hit
        self.send_request(query)

    def available_servers(self):
        '''
        :return: (list) of serves in state on-line
        '''

        # Request to get server online from Redis (from hash map)
        # Dictionary of servers online (key:val => server_id:server_name)
        servers = self.redis_conn.hgetall("servers_online")

        if servers:
            print "Servers online: " + ", ".join(list(servers.values()))
        else:
            print "All server are off-line"

        return servers

    def available_maps(self):
        '''
        Request to get available maps on the chosen server
        :return: (list) of maps
        '''
        query = pack_query(COMMAND.LIST_OF_MAPS, self.selected_server_id)

        # Put query to register a new hit
        self.send_request(query)

    def spectator_mode(self):
        # Request to server to go into spectator mode
        query = pack_query(COMMAND.SPECTATOR_MODE, self.selected_server_id, self.gui.selected_map_id)
        self.send_request(query)

    def get_existing_shots(self):
        # Request to server to go into spectator mode
        query = pack_query(COMMAND.EXISTING_SHOTS, self.selected_server_id, self.gui.selected_map_id)
        self.send_request(query)

    def players_on_map(self):
        if self.gui.selected_map_id:
            # Request to server to go into spectator mode
            query = pack_query(COMMAND.PLAYERS_ON_MAP, self.selected_server_id, self.gui.selected_map_id)
            self.send_request(query)

    def my_ships_on_map(self):
        if self.gui.selected_map_id:
            # Request to server to go into spectator mode
            query = pack_query(COMMAND.MY_SHIPS_ON_MAP, self.selected_server_id, self.gui.selected_map_id)
            self.send_request(query)

    def kick_player(self, player_id):
        '''
        :param player_id: (str) player who should be kicked from the map
        '''
        if self.gui.selected_map_id:
            data = pack_data([self.gui.selected_map_id, player_id])

            # Request to server to kick selected player
            query = pack_query(COMMAND.KICK_PLAYER, self.selected_server_id, data)
            self.send_request(query)

    def start_game(self):
        if self.gui.selected_map_id:
            # Request to server to start the game
            query = pack_query(COMMAND.START_GAME, self.selected_server_id, self.gui.selected_map_id)
            self.send_request(query)

    def restart_game(self):
        if self.gui.selected_map_id:
            # Request to server to restart the game
            query = pack_query(COMMAND.RESTART_GAME, self.selected_server_id, self.gui.selected_map_id)
            self.send_request(query)

    def disconnect_from_game(self):
        if self.gui.selected_map_id:
            # Request to server to disconnect from game
            query = pack_query(COMMAND.DISCONNECT_FROM_GAME, self.selected_server_id, self.gui.selected_map_id)
            self.send_request(query)

    def quit_from_game(self):
        if self.gui.selected_map_id:
            # Request to server to disconnect from game
            query = pack_query(COMMAND.QUIT_FROM_GAME, self.selected_server_id, self.gui.selected_map_id)
            self.send_request(query)

    # Handlers ========================================================================
    def on_response(self, channel, method, props, body):

        # print body
        # Put the task from the server into the queue (GUI should process it
        # It needs to avoid blocking some methods, because this function is running in thread
        with lock:
            self.gui.tasks.put(body)

        # Remove read msg rom queue
        channel.basic_ack(delivery_tag=method.delivery_tag)

    #############
    # Main loop for receiving notifications
    #############
    def notifications_loop(self):
        ''' Open new RabbitMQ connection to receive notifications '''

        with lock:
            host, virtual_host = self.rabbitmq["host"], self.rabbitmq["virtual_host"]
            login, password = self.rabbitmq["login"], self.rabbitmq["password"]

        try:
            print "- Start establishing connection to RabbitMQ server."

            credentials = pika.PlainCredentials(login, password)
            connection = pika.BlockingConnection(
                            pika.ConnectionParameters(host=host,
                                                      virtual_host=virtual_host,
                                                      credentials=credentials))
            channel = connection.channel()
            print "- Connection to RabbitMQ server is established."

            while self.nickname is None:
                time.sleep(0.2)
            # Bind trigger to response queue
            resp_queue = "resp_" + self.nickname

            print "Created queue for responses"

            channel.queue_declare(queue=resp_queue, durable=True)
            channel.basic_consume(self.on_response, queue=resp_queue)

            # Main loop to receive msgs
            channel.start_consuming()

            # Close MQ connection if still opened
            if not connection.is_closed:
                connection.close()
        except:
            print "ERROR (in notif. loop): Can't access RabbitMQ server, please check connection parameters."


def main():
    # Parsing arguments
    parser = ArgumentParser()

    # Args for RabbitMQ
    parser.add_argument('-rmqh', '--rabbitmq_host',
                        help='Host for RabbitMQ connection, default is %s' % RABBITMQ_HOST,
                        default=RABBITMQ_HOST)
    parser.add_argument('-rmqcr', '--rabbitmq_credentials',
                        help='Credentials for RabbitMQ connection in format "login:password",'
                             'default is %s' % RABBITMQ_CREDENTIALS,
                        default=RABBITMQ_CREDENTIALS)
    parser.add_argument('-rmqvh', '--rabbitmq_virtual_host',
                        help='Virtual host for RabbitMQ connection, default is "%s"' % RABBITMQ_VIRTUAL_HOST,
                        default=RABBITMQ_VIRTUAL_HOST)

    # Args for Redis
    parser.add_argument('-rh', '--redis_host',
                        help='Host for Redis connection, default is %s' % REDIS_HOST,
                        default=REDIS_HOST)
    parser.add_argument('-rp', '--redis_port', type=int,
                        help='Port for Redis connection, default is %d' % REDIS_PORT,
                        default=REDIS_PORT)

    parser.add_argument('-t', '--test', type=int,
                        help='Here you can test to run app on different clients. '
                             'Just add -t 1 or -t 2, or -t 3, default - %s' % 0,
                        default=0)

    args = parser.parse_args()

    # Before Client starts working, we need to check connections to RabbitMQ and Redis
    client = Client()
    gui = GUI()

    # Client can trigger GUI and vice-versa (at anytime)
    client.gui = gui
    gui.client = client

    # Save credentials for RabbitMQ
    login, password = args.rabbitmq_credentials.split(":")
    client.rabbitmq = {
        "host": args.rabbitmq_host,
        "login": login,
        "password": password,
        "virtual_host": args.rabbitmq_virtual_host
    }

    # Open connection to Redis server
    client.open_redis_connection(args.redis_host, args.redis_port)

    # Open connection to RabbitMQ server
    client.open_rabbitmq_connection()

    # If connections to RabbitMQ and Redis were established successfully, run Client
    if client.rabbitmq_connection and client.redis_conn:
        print "####################"

        # Init check name
        client.check_nickname()

        # We connected to chosen server
        # client.chosen_server_id = '1'  and client.chosen_server_id

        if client.nickname:
            # Declare queue to put requests
            request_queue = 'req_' + client.nickname
            client.rabbitmq_channel.queue_declare(queue=request_queue, durable=True)

            if args.test == 0:
                pass

            elif args.test == 1:
                client.nickname = 'rrr'
                client.selected_server_id = '2'
                client.my_player_id = 45

            elif args.test == 2:
                client.nickname = 'ff'
                client.selected_server_id = '2'
                client.my_player_id = 49

            else:
                client.nickname = 'sss'
                client.selected_server_id = '2'
                client.my_player_id = 46

            # Run servers_online window
            gui.choose_server_window()

        else:
            # Launch GUI window to enter nickname (Ask player to enter his nickname)
            gui.nickname_window()

        # Start notification loop
        notifications_thread = Thread(name='NotificationsThread', target=client.notifications_loop)
        notifications_thread.setDaemon(True)
        notifications_thread.start()

        # Run notification window (should always be opened)
        gui.notification_window()

    client.close_rabbitmq_connection()

    print 'Terminating ...'


if __name__ == "__main__":
    main()
