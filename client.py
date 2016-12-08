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
from threading import Thread
import pika  # for Msg Queue
import uuid  # for generating unique correcaltion_id
import ConfigParser as CP

# Path to the config file
current_path = os.path.abspath(os.path.dirname(__file__))
config_file = os.path.join(current_path, "config.ini")


# connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=MQ_HOST))
# channel = connection.channel()
#
#
# # Register the nickname
# nickname = "my_nickname"
#
# print nickname
#
#
# # create queue for collecting results only for this user
# result = channel.queue_declare(exclusive=True)
# callback_queue = result.method.queue
#
#
# channel.basic_publish(exchange='',
#                        routing_key='register_nickname',
#                        body=nickname,
#                        properties=pika.BasicProperties(
#                            reply_to=callback_queue,
#                            correlation_id=corr_id,
#                        ))
#
#
# channel.basic_consume(on_response, no_ack=True, queue=callback_queue)


# connection.process_data_events()
# LOG = start_logger()


# channel.start_consuming()
# connection.close()


class Client(object):
    gui = None
    connection = None
    channel = None

    nickname = None

    response = None
    corr_ids = {}

    temp_queue = None

    def __init__(self):
        # Open connection with RabbitMQ server
        self.open_connection()

        nickname = self.get_nickname()

        if not nickname:
            # Create temp queue for collecting only for register nickname for this user
            self.temp_queue = self.channel.queue_declare()
            self.temp_queue_name = self.temp_queue.method.queue
            # self.temp_queue = self.channel.queue_declare(queue="temp_queue")

            reg_me_thread = Thread(name='RegisterMeThread', target=self.reg_me_loop)
            reg_me_thread.start()

            print "Try to register nickname"

            # TODO: Create GUI window to enter nickname
            self.register_nickname("dsa")
            # self.register_nickname(nickname)

            # Blocks until the thread finished the work
            reg_me_thread.join()

        print self.nickname + "111"

        # Wait until user enters normal nickname
        while self.nickname is None:
            pass

        print "Nickname exists"

        if self.nickname:
            game_name = "test game name"
            query = pack_query(command=COMMAND.CREATE_NEW_GAME, data=game_name)

            print "Put query to register a new game"

            print 'req_' + self.nickname

            # Declare queue to put requests
            request_queue = 'req_' + self.nickname
            self.channel.queue_declare(queue=request_queue, durable=True)

            self.channel.basic_publish(exchange='',
                                       routing_key=request_queue,
                                       body=query,
                                       properties=pika.BasicProperties(
                                           reply_to='resp_' + self.nickname,
                                           delivery_mode=2
                                       ))

            notifications_thread = Thread(name='NotificationsThread', target=self.notifications_loop)
            notifications_thread.start()

            # Blocks until the thread finished the work.
            notifications_thread.join()

    def open_connection(self):
        # credentials = pika.PlainCredentials("guest", "guest")
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_HOST, credentials=credentials))

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=MQ_HOST))
        self.channel = self.connection.channel()

        # "durable" means that queue won't be lost even if RabbitMQ restarts
        self.channel.queue_declare(queue='register_nickname', durable=True)

    def close_connection(self):
        self.connection.close()

    # Generate and save corr_id into local queue corr_ids with corresponding command
    # def generate_corr_id(self, command):
    #     '''
    #     :param command: (enum)
    #     :return: (str) return generated correlation_id
    #     '''
    #     corr_id = str(uuid.uuid4())
    #     self.corr_ids[corr_id] = command
    #
    #     return corr_id

    def get_nickname(self):
        '''
        :return: (str) if nickname exists locally, return it. Otherwise False.
        '''

        # If the config exists, get the user_id from it
        if os.path.isfile(config_file):
            conf = CP.ConfigParser()
            conf.read(config_file)

            self.nickname = conf.get('USER_INFO', 'nickname')

            # TODO: Unblock the window

        return self.nickname

    def register_nickname(self, nickname):
        '''
        Register the nickname
        :param nickname: (str)
        '''
        nickname = "my_nicknam1234" + str(uuid.uuid4())

        command = COMMAND.REGISTER_NICKNAME
        query = pack_query(command, data=nickname)

        # corr_id = self.generate_corr_id(command)
        self.channel.basic_publish(exchange='',
                                   routing_key='register_nickname',
                                   body=query,
                                   properties=pika.BasicProperties(
                                       reply_to=self.temp_queue_name,
                                       # correlation_id=corr_id,
                                       delivery_mode=2
                                   ))

        # TODO: Block the window

    def save_nickname_local(self, nickname):
        '''
        Save nickname in local config

        :param nickname: (str)
        '''

        conf = CP.RawConfigParser()
        conf.add_section("USER_INFO")
        conf.set('USER_INFO', 'nickname', nickname)

        with open(config_file, 'w') as cf:
            conf.write(cf)

        # Delete temporary queue if exists
        if self.temp_queue:
            self.channel.queue_delete(queue=self.temp_queue_name)

    def on_resp_reg_me(self, channel, method, props, body):

        command, resp_code, data = parse_response(body)

        if command == COMMAND.REGISTER_NICKNAME:

            if resp_code == RESP.OK:
                print "Nickname was registered successfully"
                self.save_nickname_local(nickname=data)
                self.nickname = data

                # TODO: Unblock GUI window


                # Delete temporary queue if exists
                if self.temp_queue:
                    self.channel.queue_delete(queue=self.temp_queue_name)

                # Close reg_me connection
                self.reg_me_connection.close()

            else:
                print "Register nickname error: %s" % error_code_to_string(resp_code)

    def on_response(self, channel, method, props, body):
        # if props.correlation_id in self.corr_ids.keys():

        # Delete received response on requested command
        # command = self.corr_ids[props.correlation_id]
        # del self.corr_ids[props.correlation_id]

        print method.routing_key, body

        command, resp_code, data = parse_response(body)

        if command == COMMAND.CREATE_NEW_GAME:
            pass

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

        # Remove read msg rom queue
        channel.basic_ack(delivery_tag=method.delivery_tag)

    # def main_app_loop(self):
    #     pass
    #
    #     # self.connection.process_data_events()
    #     # channel.basic_consume(self.callback_func, result.method.queue, no_ack=True)

    def reg_me_loop(self):
        self.reg_me_connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=MQ_HOST))
        channel = self.reg_me_connection.channel()

        # Bind some triggers to queues
        channel.basic_consume(self.on_resp_reg_me, queue=self.temp_queue_name)

        channel.start_consuming()

        # Close MQ connection if still opened
        if not self.reg_me_connection.is_closed:
            self.reg_me_connection.close()

    def notifications_loop(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=MQ_HOST))
        channel = connection.channel()

        # Bind trigger to response queue
        resp_queue = "resp_" + self.nickname

        channel.queue_declare(queue=resp_queue, durable=True)
        channel.basic_consume(self.on_response, queue=resp_queue)

        channel.start_consuming()

        # Close MQ connection if still opened
        if not connection.is_closed:
            connection.close()




client = Client()

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

# client.close_connection()

print 'Terminating ...'
