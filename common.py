
# Extend PYTHONPATH for working directory----------------------------------
import os
from sys import path, argv
a_path = os.path.sep.join(os.path.abspath(argv[0]).split(os.path.sep)[:-1])
path.append(a_path)


# Constants -------------------------------------------------------------------
# Default arguments for connection to RabbitMQ servers and Redis server
RABBITMQ_HOST = "localhost"
RABBITMQ_CREDENTIALS = "guest:guest"
RABBITMQ_VIRTUAL_HOST = "/"

REDIS_HOST = "localhost"
REDIS_PORT = 6379

SEP = "|"  # separate command and data in request
SEP_DATA = ":"
# TIMEOUT = 5  # in seconds


# "Enum" for commands
def enum(**vals):
    return type('Enum', (), vals)


COMMAND = enum(
    REGISTER_NICKNAME='1',

    LIST_OF_MAPS='2',
    CREATE_NEW_GAME='3',
    JOIN_EXISTING_GAME='4',

    PLACE_SHIPS='5',
    MAKE_HIT='6',

    DISCONNECT_FROM_GAME='7',
    QUIT_FROM_GAME='8',  # after quit, user can't go back to the game

    # New funcs - only for owner
    START_GAME='9',
    RESTART_GAME='10',  # when the game ended

    KICK_PLAYER='11',

    SPECTATOR_MODE='12',
    EXISTING_SHOTS='13',

    PLAYERS_ON_MAP='14',
    MY_SHIPS_ON_MAP='15',

    # INVITE_PLAYERS='10',

    # Notifications from the server
    NOTIFICATION=enum(
        PLAYER_JOINED_TO_GAME='21',
        YOUR_SHIP_WAS_DAMAGED='22',

        # YOUR_SHIP_SANK='23',
        # SOMEONES_SHIP_SANK='24',
        SOMEONE_MADE_SHOT='25',
        YOUR_TURN_TO_MOVE='26',
        SOMEONE_TURN_TO_MOVE='27',
        YOU_ARE_KICKED='28',
        ANOTHER_PLAYER_WAS_KICKED='29',
        ANOTHER_PLAYER_DISCONNECTED='30',

        SAVE_PLAYER_ID='31',

        RESTART_GAME='32',
        GAME_STARTED='33',
        GAME_FINISHED='34'
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
    GAME_ALREADY_FINISHED='7',
    ALREADY_JOINED_TO_MAP='8',

    MAP_FULL='9',

    SHIPS_ARE_NOT_PLACED='10',  # when player joined to map, ships are not placed

    LACK_OF_PLACE_FOR_SHIPS='11',
    PLAYER_ALREADY_KICKED='12',
    NOT_ENOUGH_PLAYERS='13',  # not enough players to start the game
    YOU_ARE_IN_SPECTATOR_MODE='14',  # player can't play, only see the game
    MIN_NUMBER_OF_PLAYERS='15'  # if number of players on map is too small (case "start game" && "kick player")
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
    elif err_code == RESP.LACK_OF_PLACE_FOR_SHIPS:
        err_text = "There's no place to locate all ships"
    elif err_code == RESP.PLAYER_ALREADY_KICKED:
        err_text = "Requested player is already kicked"
    elif err_code == RESP.NOT_ENOUGH_PLAYERS:
        err_text = "Not enough players to start the game"
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
    if command == COMMAND.LIST_OF_MAPS:
        text = "List of available maps"
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
    elif command == COMMAND.SPECTATOR_MODE:
        text = "Spectator mode"
    elif command == COMMAND.EXISTING_SHOTS:
        text = "Existing shots"

    elif command == COMMAND.PLAYERS_ON_MAP:
        text = "Players on map"
    elif command == COMMAND.MY_SHIPS_ON_MAP:
        text = "My ships on map"
    # elif command == COMMAND.INVI

    # Notifications
    elif command == COMMAND.NOTIFICATION.PLAYER_JOINED_TO_GAME:
        text = "Notif. Another player joined"
    elif command == COMMAND.NOTIFICATION.YOUR_SHIP_WAS_DAMAGED:
        text = "Notif. Another player damaged my ship"
    # elif command == COMMAND.NOTIFICATION.YOUR_SHIP_SANK:
    #     text = "Notif. My ship sank"
    # elif command == COMMAND.NOTIFICATION.SOMEONES_SHIP_SANK:
    #     text = "Notif. Another player damaged another player's ship"
    elif command == COMMAND.NOTIFICATION.SOMEONE_MADE_SHOT:
        text = "Notif. Someone made a shot"
    elif command == COMMAND.NOTIFICATION.YOUR_TURN_TO_MOVE:
        text = "Notif. My turn to move"
    elif command == COMMAND.NOTIFICATION.YOU_ARE_KICKED:
        text = "Notif. You're kicked from the map"
    elif command == COMMAND.NOTIFICATION.SAVE_PLAYER_ID:
        text = "Notif. Save your player_id"
    elif command == COMMAND.NOTIFICATION.RESTART_GAME:
        text = "Notif. Restart the game"
    elif command == COMMAND.NOTIFICATION.GAME_STARTED:
        text = "Notif. Game finished"
    elif command == COMMAND.NOTIFICATION.GAME_FINISHED:
        text = "Notif. Game started"
    return text


def pack_query(command, server_id="", data=""):
    '''
    :param data: (list) to pack
    :param server_id: (str) server_id that should process request
    :return: packed elements from the list separated by separator
    '''
    return SEP.join([command, str(server_id), str(data)])


def pack_resp(command, resp_code, server_id="", data=""):
    '''
    :param data: (list) to pack
    :return: packed elements from the list separated by separator
    '''
    return SEP.join([str(command), str(resp_code), str(server_id), str(data)])


def pack_data(data):
    '''
    :param data: (list) of values to pack
    :return: (str) - packed data joined by SEP_DATA separator
    '''
    data = [str(el) for el in data]
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


# Check that connection with Redis is alive
def check_redis_connection(redis_connection):
    try:
        r_ping = redis_connection.ping()
    except:
        r_ping = False
        print "ERROR: Can't access Redis server, please check connection parameters"
    return r_ping

