
# Extend PYTHONPATH for working directory----------------------------------
import os
from sys import path, argv
a_path = os.path.sep.join(os.path.abspath(argv[0]).split(os.path.sep)[:-1])
path.append(a_path)


# Constants -------------------------------------------------------------------
MQ_HOST = "localhost"
MQ_PORT = 15672
SEP = "|"  # separate command and data in request
SEP_DATA = ":"
# TIMEOUT = 5  # in seconds


# "Enum" for commands
def enum(**vals):
    return type('Enum', (), vals)


COMMAND = enum(
    REGISTER_NICKNAME='1',
    CREATE_NEW_GAME='2',
    JOIN_EXISTING_GAME='3',

    PLACE_SHIPS='4',
    MAKE_HIT='5',

    DISCONNECT_FROM_GAME='6',
    QUIT_FROM_GAME='7',  # after quit, user can't go back to the game

    # New funcs - only for owner
    START_GAME='8',
    RESTART_GAME='9',  # when the game ended

    KICK_PLAYER='10',
    # INVITE_PLAYERS='10',

    # Notifications from the server
    NOTIFICATION=enum(
        PLAYER_JOINED_TO_GAME='21',
        YOUR_SHIP_WAS_DAMAGED='22',
        # YOUR_SHIP_SANK='23',
        SOMEONES_SHIP_SANK='24',
        YOUR_TURN_TO_MOVE='25',
        YOU_ARE_KICKED='26',

        SERVER_ONLINE='27'
    )
)


# Responses
RESP = enum(
    OK='0',
    FAIL='1',
    NICKNAME_ALREADY_EXISTS='2',
    SHOT_WAS_ALREADY_MADE_HERE='3',
    MAP_NAME_ALREADY_EXISTS='4',
    MAP_DOES_NOT_EXIST='5',
    GAME_ALREADY_STARTED='6',
    ALREADY_JOINED_TO_MAP='7'
)


# Main functions ---------------------------------------------------------------
def error_code_to_string(err_code):
    '''
    :param err_code: code of the error
    :return: (string) defenition of the error
    '''
    global RESP

    err_text = ""

    if err_code == RESP.OK:
        err_text = "No errors"
    elif err_code == RESP.FAIL:
        err_text = "Bad result"
    elif err_code == RESP.NICKNAME_ALREADY_EXISTS:
        err_text = "Requested nickname already exists"
    elif err_code == RESP.SHOT_WAS_ALREADY_MADE_HERE:
        err_text = "Shot was already made here"
    elif err_code == RESP.MAP_NAME_ALREADY_EXISTS:
        err_text = "Given map name already exists"
    elif err_code == RESP.MAP_DOES_NOT_EXIST:
        err_text = "Given map doesn't exist"
    elif err_code == RESP.GAME_ALREADY_STARTED:
        err_text = "Game already started"
    elif err_code == RESP.ALREADY_JOINED_TO_MAP:
        err_text = "You already joined to requested map"
    return err_text


def command_to_str(command):
    '''
    Convert command into the string

    :param command: (str) - command code from enum COMMAND
    :return text: (str) - explanation of the command
    '''
    global COMMAND

    text = ""

    if command == COMMAND.REGISTER_NICKNAME:
        text = "Register nickname"
    elif command == COMMAND.CREATE_NEW_GAME:
        text = "Create new game"
    elif command == COMMAND.JOIN_EXISTING_GAME:
        text = "Join existing game"
    elif command == COMMAND.PLACE_SHIPS:
        text = "Place ship"
    elif command == COMMAND.MAKE_HIT:
        text = "Make shot"
    elif command == COMMAND.DISCONNECT_FROM_GAME:
        text = "Disconnect from the game"
    elif command == COMMAND.QUIT_FROM_GAME:
        text = "Quit from the game"
    elif command == COMMAND.START_GAME:
        text = "Start game"
    elif command == COMMAND.RESTART_GAME:
        text = "Restart the game"
    elif command == COMMAND.KICK_PLAYER:
        text = "Kick player"
    # elif command == COMMAND.INVI


    # Notifications
    elif command == COMMAND.NOTIFICATION.PLAYER_JOINED_TO_GAME:
        text = "Notif. Another player joined"
    elif command == COMMAND.NOTIFICATION.YOUR_SHIP_WAS_DAMAGED:
        text = "Notif. Another player damaged my ship"
    # elif command == COMMAND.NOTIFICATION.YOUR_SHIP_SANK:
    #     text = "Notif. My ship sank"
    elif command == COMMAND.NOTIFICATION.SOMEONES_SHIP_SANK:
        text = "Notif. Another player damaged another player's ship"
    elif command == COMMAND.NOTIFICATION.YOUR_TURN_TO_MOVE:
        text = "Notif. My turn to move"
    elif command == COMMAND.NOTIFICATION.YOU_ARE_KICKED:
        text = "Notif. You're kicked from the map"
    elif command == COMMAND.NOTIFICATION.SERVER_ONLINE:
        text = "Notif. Server become online"

    return text


def pack_query(command, server_id="", data=""):
    '''
    :param data: (list) to pack
    :param server_id: (str) server_id that should process request
    :return: packed elements from the list separated by separator
    '''
    return SEP.join([command, server_id, data])


def pack_resp(command, resp_code, server_id="", data=""):
    '''
    :param data: (list) to pack
    :return: packed elements from the list separated by separator
    '''
    return SEP.join([command, resp_code, server_id, data])


def pack_data(data):
    '''
    :param data: (list) of values to pack
    :return: (str) - packed data joined by SEP_DATA separator
    '''
    return SEP_DATA.join(data)


def parse_query(raw_data):
    '''
    :param raw_data: string that may contain command and data
    :return: (command, data)
    '''
    # Split string by separator to get the command and data
    server_id, command, data = raw_data.split(SEP)
    return server_id, command, data


def parse_response(raw_response):
    '''
    :param raw_data: string that may contain command and data
    :return: (command, data)
    '''
    # Split string by separator to get the command and data
    command, resp_code, server_id, data = raw_response.split(SEP)
    return command, resp_code, server_id, data


def parse_data(raw_data):
    '''
    :param raw_data: (str)
    :return: (list)
    '''
    # Split string by SEP_DATA separator to get data list from raw_data
    return raw_data.split(SEP_DATA)
