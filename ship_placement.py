import numpy as np
# import pylab as plt
from models import *
from common import RESP, pack_data
from collections import defaultdict
from random import randint
from server import refresh_db_connection


# N  = int(math.ceil(math.sqrt(100 * players)))

@refresh_db_connection
def place_ships(map_id, player_id):
    '''
    Main function to place ships (randomly).
    It iterates over 4 possible ship types (and their quantity)
    and try to locate them among existing ships on the map

    :param map_id:
    :param player_id:
    :return: resp_code
    '''
    resp_code, query = RESP.OK, ""

    # Get map size by map_id (from DB)
    # print map_id
    game_map = Map.get(Map.map_id == map_id)
    # print MAP_DOES_NOT_EXIST
    rows, columns = game_map.rows, game_map.columns  # equal to n, m

    # Player already placed his ships
    if Ship_to_map.select().where(Ship_to_map.map == map_id, Ship_to_map.player == player_id).count():
        # Delete his previous ships locations in DB
        Ship_to_map.delete().where(Ship_to_map.map == map_id, Ship_to_map.player == player_id).execute()

    # Empty board (indexes start from [0,0] to [n-1,m-1]
    board = np.zeros((rows, columns), dtype=np.int)

    # Read already existing ships from DB
    for ship_obj in Ship_to_map.select().where(Ship_to_map.map == map_id):
        x1, x2 = ship_obj.row_start, ship_obj.row_end
        y1, y2 = ship_obj.column_start, ship_obj.column_end

        # make zone, where player can't place ships
        zone_x1, zone_y1 = x1, y1

        # Fix to avoid negative coordinates
        zone_x1 = 1 if zone_x1 < 1 else zone_x1
        zone_y1 = 1 if zone_y1 < 1 else zone_y1

        board[zone_x1 - 1:x2 + 2, zone_y1 - 1:y2 + 2] = 1

        # Place existing ships
        board[x1:x2 + 1, y1:y2 + 1] = 2

        # print x1 - 1, x2 + 2, y1 - 1, y2 + 1
        # print board

    new_ships = []
    new_ships_data = []
    ships = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]

    # Iterate from biggest to smallest
    for ship_size in ships[::-1]:
        # Chose random direction, if 0 - horizontal, 1 - vertical
        direction = randint(0, 1)

        possible_locations = get_locations(board, direction, ship_size, rows, columns)

        # If there's no place for this direction, then change direction
        if len(possible_locations) == 0:

            # Try to find place in another direction direction
            new_direction = 0 if direction == 1 else 1
            possible_locations = get_locations(board, new_direction, ship_size, rows, columns)

            if len(possible_locations) == 0:
                resp_code = RESP.LACK_OF_PLACE_FOR_SHIPS
                print("Can't place all ships for this player")
                break

        keys = list(possible_locations.keys())
        rand_row = keys[randint(0, len(keys) - 1)]

        vals = possible_locations[rand_row]
        rand_col = vals[randint(0, len(vals) - 1)]

        if direction == 0:
            x1, x2, y1, y2 = (rand_row, rand_row, rand_col, rand_col + ship_size - 1)
        else:
            x1, x2, y1, y2 = (rand_row, rand_row + ship_size - 1, rand_col, rand_col)

        # make zone, where player can't place ships
        zone_x1, zone_y1 = x1, y1

        # Fix to avoid negative coordinates
        zone_x1 = 1 if zone_x1 < 1 else zone_x1
        zone_y1 = 1 if zone_y1 < 1 else zone_y1

        board[zone_x1 - 1:x2 + 2, zone_y1 - 1:y2 + 2] = 1

        # Place this ship
        board[x1:x2 + 1, y1:y2 + 1] = 2

        # Collect new ship coordinate to save them later in DB
        ship_coord = (x1, x2, y1, y2, ship_size)
        new_ships.append(ship_coord)

        # For compressed query
        for el in zip(ship_coord):
            new_ships_data.append(str(el[0]))

        # print(x1, x2, y1, y2, "Ship type: %s" % ship_size)
    else:
        print("All ships placed successfully.")

        # Save new ships in DB
        for x1, x2, y1, y2, ship_size in new_ships:
            Ship_to_map.create(map=map_id,
                               player=player_id,
                               row_start=x1,
                               row_end=x2,
                               column_start=y1,
                               column_end=y2,
                               ship_type=ship_size)
        # plt.matshow(board)
        # plt.show()

    data = pack_data(new_ships_data)
    return resp_code, data


def get_locations(board, direction, ship_size, rows, columns):
    '''
    Get possible locations to place ships for a particular direction

    :param direction: (int) (0 - horizontal, 1 - vertical)
    :return: (dict) with coordinates key = row, value = column
    '''
    possible_locations = defaultdict(list)  # row => columns (list)

    # Iterate horizontally
    if direction == 0:
        for i in range(rows):
            for j in range(columns):
                # print(i)
                if board[i, j] == 0 \
                        and len(board[i, j:j + ship_size]) == ship_size \
                        and all(v == 0 for v in board[i, j:j + ship_size]):
                    possible_locations[i].append(j)
                    # print i, j
                    # print board[i, j:j+ship_size], ship_size, i, j, rows, columns

    # Iterate vertically
    else:
        for j in range(columns):
            for i in range(rows):
                if board[i, j] == 0 \
                        and len(board[i:i + ship_size, j]) == ship_size \
                        and all(v == 0 for v in board[i:i + ship_size, j]):
                    # print(i, j)
                    possible_locations[i].append(j)
                    # print i, j
    return possible_locations
