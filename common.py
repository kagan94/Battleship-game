
SEP = "|"  # separate command and data in request
# TIMEOUT = 5  # in seconds


# "Enum" for commands
def enum(**vals):
    return type('Enum', (), vals)


COMMAND = enum(
    REGISTER_NICKNAME='1',
    CREATE_NEW_GAME='2',
    JOIN_EXISTING_GAME='3',

    PLACE_SHIP='2',
    MAKE_HIT='4',

    DISCONNECT_FROM_GAME='5',
    QUIT_FROM_GAME='6',  # after quit, user can't go back to the game

    # New funcs - only for owner
    START_GAME='2',
    RESTART_GAME='2',  # when the game ended
    INVITE_PLAYERS='2',

    # Notifications from the server
    # NOTIFICATION=enum(
    #     UPDATE_FILE='9',
    #     FILE_CREATION='10',
    #     FILE_DELETION='11',
    #     CHANGED_ACCESS_TO_FILE='12'
    # )
)

# Responses
RESP = enum(
    OK='0',
    FAIL='1',
    NICKNAME_ALREADY_EXISTS='2'
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
        err_text = "Bad result."
    elif err_code == RESP.PERMISSION_ERROR:
        err_text = "Permissions error."
    elif err_code == RESP.NICKNAME_ALREADY_EXISTS:
        err_text = "Requested nickname already exists."

    return err_text


def pack_resp(command, resp_code, data=""):
    '''
    :param data: (list) to pack
    :return: packed elements from the list separated by separator
    '''
    return SEP.join([command, resp_code, data])


def parse_query(raw_data):
    '''
    :param raw_data: string that may contain command and data
    :return: (command, data)
    '''
    # Split string by separator to get the command and data
    command, data = raw_data.split(SEP)
    return command, data


def parse_response(raw_data):
    '''
    :param raw_data: string that may contain command and data
    :return: (command, data)
    '''
    # Split string by separator to get the command and data
    command, resp_code, data = raw_data.split(SEP)
    return command, resp_code, data
