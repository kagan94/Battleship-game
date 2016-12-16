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

DELETE_ALL_QUEUES()


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

        self.my_player_id = None

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
    def get_damaged_player_id_by_shot(self, map_id, row, column):

        # Check if someone stayed in this region, if yes hit = 1, otherwise hit = 0
        # (whether hit was successful or not)
        # print row, column
        hit_query = Ship_to_map.select().where(Ship_to_map.map == map_id,
                                               # Check by row
                                               Ship_to_map.row_start <= row, Ship_to_map.row_end >= row,
                                               # Check by column
                                               Ship_to_map.column_start <= column, Ship_to_map.column_end >= column)
        # try:
        #     record = hit_query.get()
        #     return record.player.player_id
        # # Nobody was damaged
        # except Ship_to_map.DoesNotExist:
        #     return None

        # try:
        # print map_id
        # print record, record.player.player_id, "xxxxxxxxxx"
        record = hit_query.get()
        return record.player.player_id
        # Nobody was damaged
        # except Ship_to_map.DoesNotExist:
        #     return None

    @refresh_db_connection
    def existing_shots(self, map_id):
        ''' Sends existing shots to player '''

        # Compressed data in format (target_row, target_column, hit_successful, damaged_player_id)
        shots_data = []

        # Get all games which have not been started yet
        shots_query = Player_hits.select().where(Player_hits.map)

        for s in shots_query:
            # Compress data
            if s.hit == "1":
                # print "sss, ", s.hit
                damaged_player_id = self.get_damaged_player_id_by_shot(map_id, s.row, s.column)
            else:
                damaged_player_id = "-"

            # print damaged_player_id

            shot = (s.map_id, s.row, s.column, s.hit, damaged_player_id)
            for el in zip(shot):
                shots_data.append(str(el[0]))

        data = pack_data(shots_data)
        return data

    @refresh_db_connection
    def another_player_made_shot(self, map_id, initiator_id, row, column, damaged_player_id):
        ''' Player made a shot, then notify other players about this shot (except player_id) '''

        if damaged_player_id == "":
            damaged_player_id = 0

        # Get all players on this map (except initiator and disconnected users)
        players_on_map_query = Player_to_map.select().where(
                Player_to_map.map == map_id,
                ~(Player_to_map.player << [initiator_id, damaged_player_id]),
                Player_to_map.disconnected == 0)

        print "SOMEONE_MADE_SHOT", players_on_map_query.count()

        # Send notification about this move
        for record in players_on_map_query:

            data = pack_data([map_id, initiator_id, row, column])
            query = pack_resp(COMMAND.NOTIFICATION.SOMEONE_MADE_SHOT, RESP.OK, self.server_id, data)

            # print record.player.nickname
            # Put notification into the queue
            self.send_response(nickname=record.player.nickname, query=query)

    @refresh_db_connection
    def is_game_end(self, map_id):
        def remaining_players_on_map(map_id):
            '''
            :param map_id: (str)
            :return: (list) of players_ids which are still playing on the map
                     (Means have ships on the map, which are not destroyed)
            '''

            query = Ship_to_map.select(Ship_to_map.player_id).distinct().where(
                Ship_to_map.map == map_id,
                Ship_to_map.totally_sank == "0"
            )

            # Return list of remaining_players
            return [record.player_id for record in query]

        remaining_players = remaining_players_on_map(map_id)

        query = Player_to_map.select().distinct().where(
            Player_to_map.map == map_id,
            Player_to_map.player << remaining_players
        )

        game_end = False

        if query.count() < 2:
            game_end = True

        return game_end

    @refresh_db_connection
    def find_next_player(self, map_id, current_player_id):
        '''
        Find next player, by current player_id.

        :param map_id: (str)
        :param current_player_id: (str)
        :return: next_player_id(int), next_player_nickname (str)
        '''

        players = Player_to_map.select().where(Player_to_map.map == map_id).order_by(Player_to_map.id)

        players_nicknames = [p.player.nickname for p in players]
        players = [p.player_id for p in players]

        try:
            key = players.index(current_player_id)
        except ValueError:
            return None, None

        # if it was the last player, then choose the 1st
        if key + 1 >= len(players):
            next_player_id = players[0]
            next_player_nickname = players_nicknames[0]

        # Otherwise, choose next player
        else:
            next_player_id = players[key + 1]
            next_player_nickname = players_nicknames[key + 1]

        return next_player_id, next_player_nickname

    @refresh_db_connection
    def kick_player(self, map_id, player_id_to_kick):
        '''
        :param map_id:
        :param player_id_to_kick:
        :return: resp_code, player_nickname
        '''
        resp_code, player_nickname = RESP.OK, ""

        query = Player_to_map.select().where(
            Player_to_map.player == player_id_to_kick,
            Player_to_map.map == map_id
        )

        if query.count():
            player_nickname = query.get().player.nickname

            # Delete record from DB
            query.delete_instance()

            # send notification to player that was kicked
            query = pack_resp(COMMAND.NOTIFICATION.YOU_ARE_KICKED, RESP.OK, self.server_id, data=map_id)
            self.send_response(nickname=player_nickname, query=query)

            # TODO: Add notification to other players that this player was kicked

        else:
            resp_code = RESP.PLAYER_ALREADY_KICKED

        return resp_code, player_id_to_kick

    @refresh_db_connection
    def make_hit(self, map_id, player_id, target_row, target_column):
        '''
        :param map_id: (str)
        :param player_id: (int)
        :param row: (str) x = coordinate where player made a shot
        :param column: (str) y = coordinate where player made a shot
        :return: (enum) = response code, (str) = result of shot (0 = missed, 1 = hit)
        '''
        # map_id, row, column = [int(v) for v in [map_id, row, column]]
        # is_game_end can be "0" or "1"
        resp_code, hit, is_game_end = RESP.OK, "0", ""
        damaged_player_id = ""

        hit_record = None

        # Map doesn't exist
        if not self.map_exists(map_id):
            resp_code = RESP.MAP_DOES_NOT_EXIST

        # Player already made shot in this region
        elif Player_hits.select().where(Player_hits.map == map_id,
                                        Player_hits.row == target_row,
                                        Player_hits.column == target_column).count() > 0:
            resp_code = RESP.SHOT_WAS_ALREADY_MADE_HERE

        # Register new shot
        else:

            #####################
            # Check if someone stayed in this region, if yes hit = 1, otherwise hit = 0
            # (whether hit was successful or not)
            hit_query = Ship_to_map.select().where(Ship_to_map.player != player_id,
                                                   Ship_to_map.map == map_id,
                                                   # Check by row
                                                   Ship_to_map.row_start <= target_row,
                                                   Ship_to_map.row_end >= target_row,
                                                   # And by column
                                                   Ship_to_map.column_start <= target_column,
                                                   Ship_to_map.column_end >= target_column)
            try:
                hit_record = hit_query.get()
                hit = "1"

                # Notify player whose ship was damaged
                self.notify_about_ship_damage(map_id,
                                              initiator_id=player_id,
                                              target_player_name=hit_record.player.nickname,
                                              target_row=target_row,
                                              target_column=target_column)

                # Player who was damaged
                damaged_player_id = hit_record.player.player_id

            # Nobody was damaged
            except Ship_to_map.DoesNotExist:
                pass

            # Register hit in DB
            shot_query = Player_hits(map=map_id, player=player_id,
                                     row=int(target_row), column=int(target_column),
                                     hit=hit)
            shot_query.save()

            #######################################
            # Notify next player about his turn
            if hit == "0":
                next_player_id, next_player_nickname = self.find_next_player(map_id, current_player_id=player_id)

                if next_player_id is not None:
                    query = pack_resp(COMMAND.NOTIFICATION.YOUR_TURN_TO_MOVE, RESP.OK, self.server_id)
                    self.send_response(nickname=next_player_nickname, query=query)

            # Check whether the shot completely destroyed ship or not
            # Here we mark ship as totally sank
            else:
                # Update location of the shot that caused damage
                shot_query.ship_location_id = hit_record.location_id
                shot_query.save()

                # Get damaged ship record
                damaged_ship_record = Ship_to_map.get(location_id=hit_record.location_id)
                ship_size = damaged_ship_record.ship_type

                # Get all shots in this ship
                all_shots_in_ship = Player_hits.select().where(Player_hits.ship_location_id == hit_record.location_id)

                # Update saved shot in case the ship was totally destroyed
                if all_shots_in_ship.count() >= ship_size:
                    damaged_ship_record.totally_sank = 1
                    damaged_ship_record.save()

            #######################################
            # Notify other players about this shot in any case
            self.another_player_made_shot(map_id, player_id, target_row, target_column, damaged_player_id)

            # is_game_end() return True/False
            game_finished = self.is_game_end(map_id)

            # If game finished, notify all players about it
            if game_finished:
                m = Map.select().where(Map.map_id == map_id).get()

                # Mark that the map as finished (code = 2)
                m.game_started = 2
                m.save()

                all_players = Player_to_map.select().where(Map.map_id == map_id)
                data = pack_data([map_id, m.owner_id])

                # Put notification about game end into the RabbitMQ
                for record in all_players:
                    query = pack_resp(COMMAND.NOTIFICATION.GAME_FINISHED, RESP.OK, self.server_id, data)
                    self.send_response(nickname=record.player.nickname, query=query)

        return resp_code, hit, damaged_player_id

    @refresh_db_connection
    def kick_player(self, map_id, player_id_to_kick):
        '''
        :param map_id:
        :param player_id_to_kick:
        :return: resp_code, player_nickname
        '''
        resp_code, player_nickname = RESP.OK, ""

        query = Player_to_map.select().where(
            Player_to_map.player == player_id_to_kick,
            Player_to_map.map == map_id
        )

        if query.count():
            player = query.get()
            player_nickname = player.player.nickname

            # Delete record from DB
            player.delete_instance()

            # send notification to player that was kicked
            query = pack_resp(COMMAND.NOTIFICATION.YOU_ARE_KICKED, RESP.OK, self.server_id, data=map_id)
            self.send_response(nickname=player_nickname, query=query)

            # TODO: Add notification to other players that this player was kicked

        else:
            resp_code = RESP.PLAYER_ALREADY_KICKED

        return resp_code, player_id_to_kick

    @refresh_db_connection
    def start_game(self, initiator_id, map_id):
        ''' Map creator triggered to start game '''
        resp_code = RESP.OK

        current_map = Map.select().where(Map.map_id == map_id).get()
        all_players = Player_to_map.select().where(Player_to_map.map == map_id)
        # TODO: add check that there should be at least 2 people on the map before the game can start

        # Not enough players to start the game
        if all_players.count() < 2:
            resp_code = RESP.NOT_ENOUGH_PLAYERS

        # If game has not been started yet
        elif not current_map.game_started:
            normal_players = Player_to_map.select().where(
                Player_to_map.player.in_(
                    Ship_to_map.select(Ship_to_map.player_id).where(
                        Ship_to_map.map == Player_to_map.map
                    )
                ),
                Player_to_map.map_id == map_id,
                Player_to_map.player != initiator_id
            )

            # These players will start to play now
            for record in normal_players:
                # Notify players on this map that game started
                query = pack_resp(COMMAND.NOTIFICATION.GAME_STARTED, RESP.OK, self.server_id, data=map_id)
                self.send_response(nickname=record.player.nickname, query=query)

            # Notify players who didn't place ships that they kicked
            players_to_kick = Player_to_map.select().where(
                Player_to_map.player.not_in(
                    Ship_to_map.select(Ship_to_map.player_id).where(
                        Ship_to_map.map == Player_to_map.map
                    )
                ),
                Player_to_map.map_id == map_id,
                Player_to_map.player != initiator_id
            )

            # These players will be kicked now
            for p in players_to_kick:
                # Trigger notification method to notify kicked player
                self.notify_about_kick(map_id, p.player.nickname)

            # Update record in DB that game started
            current_map.game_started = 1
            current_map.save()

        else:
            resp_code = RESP.GAME_ALREADY_STARTED

        return resp_code

    @refresh_db_connection
    def create_new_map(self, owner_id, name, size):
        '''
        Create a new map with size of (rows x columns)

        :param owner_id: (int)
        :param name: (str) = map name
        :param size: (str)
        :return: (enum) = response code, (str) map_id
        '''
        resp_code, map_id = RESP.OK, ""

        # Check that map with the same name doesn't exist in DB
        if Map.select().where(Map.name == name, Map.server == self.server_id).count() == 0:

            # 120 - is the number of cells needed to place all ships for 1 player
            max_players = (int(size) ** 2) / 120

            # Create new map
            Map.create(owner=owner_id, server=self.server_id, name=name, size=size, max_players=max_players)
            map_id = Map.select().order_by(Map.map_id.desc()).get().map_id

            # Add player to map and mark that it's his turn to move
            Player_to_map.create(map=map_id, player=owner_id, my_turn=1)

        else:
            resp_code = RESP.MAP_NAME_ALREADY_EXISTS

        data = pack_data([map_id, name, size])
        return resp_code, data

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

        my_turn = "0"
        ships_already_placed = "0"
        game_already_started = "0"
        owner_id = ""

        game_started = Map.select().where(
            Map.map_id == map_id,
            Map.server == self.server_id,
            Map.game_started == 1
        ).count() > 0

        # Query to check does player already place his ships
        ships_placed = Ship_to_map.select().where(
            Ship_to_map.map == map_id,
            Ship_to_map.player == player_id
        ).count() > 0

        already_joined = Player_to_map.select().where(
            Player_to_map.map == map_id,
            Player_to_map.player == player_id
        )

        # Map doesn't exist
        if not self.map_exists(map_id):
            resp_code = RESP.MAP_DOES_NOT_EXIST

        # TODO: Add check on spectator mode
        else:
            map_info = Map.get(Map.map_id == map_id, Map.server == self.server_id)
            owner_id = map_info.owner.player_id

            # All players on this map
            all_players = Player_to_map.select().where(Player_to_map.map == map_id)

            if ships_placed:
                ships_already_placed = "1"

            ###########
            # Game started (negative response)
            if game_started and not already_joined.count() > 0:
                resp_code = RESP.GAME_ALREADY_STARTED

            elif game_started and already_joined.count() > 0:
                resp_code = RESP.ALREADY_JOINED_TO_MAP
                game_already_started = "1"

                self.mark_player_as_connected(map_id, player_id)

                if already_joined.get().my_turn:
                    my_turn = "1"

            ###########
            # Game didn't started
            elif not game_started and already_joined.count() > 0:
                self.mark_player_as_connected(map_id, player_id)

            elif not game_started and not already_joined.count() > 0:

                # Exceeding limit of players
                if map_info.max_players >= all_players.count() + 1:
                    resp_code = RESP.MAP_FULL

                # Add player to the map
                # (Player hasn't joined this map yet)
                else:
                    Player_to_map.create(map_id=map_id, player=player_id)

                    # Notify all players (except this) about joining to the map
                    # Check that current player and creator of the map are different players
                    for record in all_players:
                        if record.player.player_id != player_id:
                            query = pack_resp(COMMAND.NOTIFICATION.PLAYER_JOINED_TO_GAME,
                                              RESP.OK, data=pack_data([player_id, player_nickname]))
                            self.send_response(record.player.nickname, query)

        data = pack_data([my_turn, ships_already_placed, game_already_started, owner_id])
        return resp_code, data

    @refresh_db_connection
    def list_of_maps(self):
        '''
        :return: (data) - packed data in format (map_id, map_name, rows, columns)
        '''
        data = ""
        maps_data = []

        # Get all games which have not been started yet
        maps_query = Map.select().where(Map.server == self.server_id)
                                        # Map.game_started == 0)

        for m in maps_query:
            # Compress data
            map_data = (m.map_id, m.name, m.size)
            for el in zip(map_data):
                maps_data.append(str(el[0]))

        data = pack_data(maps_data)
        return RESP.OK, data

    @refresh_db_connection
    def spectator_mode(self, player_id, map_id):
        ''' Fetch all ships locations and send them to user in spectator mode '''
        resp_code = RESP.OK

        all_ships = []
        all_ships_query = Ship_to_map.select().where(Ship_to_map.map == map_id)

        for ship in all_ships_query:
            x1, x2 = ship.row_start, ship.row_end
            y1, y2 = ship.column_start, ship.column_end

            ship_coord = (ship.player_id, x1, x2, y1, y2, ship.ship_type)

            # Compress data
            for el in zip(ship_coord):
                all_ships.append(str(el[0]))

        data = pack_data(all_ships)
        return resp_code, data

    @refresh_db_connection
    def players_on_map(self, player_id, map_id):
        ''' Return a compressed string (list of current players on requested map) '''

        players_data = []

        # Get all players on map except who requested this command
        players_query = Player_to_map.select().where(Player_to_map.map == map_id,
                                                     Player_to_map.player != player_id)

        for p in players_query:
            # Compress data
            disconnected = p.disconnected if p.disconnected is not None else "0"
            player_data = (p.map_id, p.player_id, p.player.nickname, disconnected)

            for el in zip(player_data):
                players_data.append(str(el[0]))

        data = pack_data(players_data)

        return data

    @refresh_db_connection
    def my_ships_on_map(self, player_id, map_id):
        ''' Return compressed str (list of ships locations for particular player '''
        resp_code, ships_data = RESP.OK, []

        # Get all games which have not been started yet
        ships_query = Ship_to_map.select().where(Ship_to_map.map == map_id,
                                                 Ship_to_map.player_id == player_id)

        for s in ships_query:
            # Compress data
            ship_data = (map_id, s.row_start, s.row_end, s.column_start, s.column_end, s.ship_type, s.totally_sank)
            for el in zip(ship_data):
                ships_data.append(str(el[0]))

        data = pack_data(ships_data)
        return resp_code, data

    @refresh_db_connection
    def disconnect_from_game(self, map_id, player_id):
        ''' Player can be disconnected, but he/she continues to play '''
        resp_code = RESP.OK

        Player_to_map.update(disconnected=1)\
            .where(Player_to_map.map == map_id, Player_to_map.player == player_id).execute()

        return resp_code

    @refresh_db_connection
    def mark_player_as_connected(self, map_id, player_id):
        ''' Mark player as connected '''
        Player_to_map.update(disconnected=0)\
            .where(Player_to_map.map == map_id, Player_to_map.player == player_id).execute()

    ###################
    # Notifications
    ###################
    def notify_about_ship_damage(self, map_id, initiator_id, target_player_name, target_row, target_column):
        ''' Send notification to damaged player '''

        data = pack_data([map_id, initiator_id, target_row, target_column])
        query = pack_resp(COMMAND.NOTIFICATION.YOUR_SHIP_WAS_DAMAGED, RESP.OK, self.server_id, data)

        # Put notification into the queue
        self.send_response(nickname=target_player_name, query=query)

    def notify_about_kick(self, map_id, player_nickname):
        ''' This player will be kicked now '''

        query = pack_resp(COMMAND.NOTIFICATION.YOU_ARE_KICKED, RESP.OK, self.server_id, data=map_id)

        # Put notification into the queue
        self.send_response(nickname=player_nickname, query=query)

    ###################
    # Handlers for queue ===================================================================================
    ###################
    def on_register_nickname(self, ch, method, props, body):
        print(">> Received command to register nickname: %s" % body)

        command, server_id, nickname = parse_query(body)

        resp_code = self.register_nickname(nickname)
        response = pack_resp(COMMAND.REGISTER_NICKNAME, resp_code, self.server_id, data=nickname)

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
        :param props: (properties)
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

            # Additional notification to send player_id
            additional_query = pack_resp(
                COMMAND.NOTIFICATION.SAVE_PLAYER_ID, RESP.OK, self.server_id, player_id)
            self.send_response(nickname=nickname, query=additional_query)

        # +
        elif command == COMMAND.CREATE_NEW_GAME:
            game_name, field_size = parse_data(data)

            resp_code, data = self.create_new_map(owner_id=player_id, name=game_name, size=field_size)
            query = pack_resp(command, resp_code, self.server_id, data)

        # +
        elif command == COMMAND.JOIN_EXISTING_GAME:
            resp_code, data = self.join_game(map_id=data, player_id=player_id, player_nickname=nickname)
            query = pack_resp(command, resp_code, self.server_id, data)

        # +
        elif command == COMMAND.PLACE_SHIPS:
            resp_code, data = place_ships(map_id=data, player_id=player_id)
            query = pack_resp(command, resp_code, self.server_id, data)

        # +
        elif command == COMMAND.MAKE_HIT:
            map_id, row, column = parse_data(data)

            resp_code, hit_successful, damaged_player_id = self.make_hit(map_id, player_id, row, column)

            # Prepare query and data
            data = pack_data([row, column, hit_successful, damaged_player_id])
            query = pack_resp(command, resp_code, self.server_id, data)

        elif command == COMMAND.DISCONNECT_FROM_GAME:
            map_id = data

            resp_code = self.disconnect_from_game(map_id, player_id)
            query = pack_resp(command, resp_code, self.server_id, data=map_id)

        elif command == COMMAND.QUIT_FROM_GAME:
            pass

        # +
        elif command == COMMAND.START_GAME:
            map_id = data

            resp_code = self.start_game(player_id, map_id)
            query = pack_resp(command, resp_code, self.server_id, map_id)

        elif command == COMMAND.RESTART_GAME:
            pass

        # +
        elif command == COMMAND.KICK_PLAYER:
            map_id, player_id_to_kick = parse_data(data)

            resp_code, player_id_to_kick = self.kick_player(map_id, player_id_to_kick)
            query = pack_resp(command, RESP.OK, self.server_id, data=player_id_to_kick)

        # +
        elif command == COMMAND.PLAYERS_ON_MAP:
            ''' List of all players on the map (including disconnected)'''
            data = self.players_on_map(player_id, map_id=data)
            query = pack_resp(command, RESP.OK, self.server_id, data)

        elif command == COMMAND.MY_SHIPS_ON_MAP:
            ''' List of all players on the map (including disconnected)'''
            resp_code, data = self.my_ships_on_map(player_id, map_id=data)
            query = pack_resp(command, resp_code, self.server_id, data)

        elif command == COMMAND.SPECTATOR_MODE:
            # Spectator mode. Player can see all ships
            # But he can't take part in the game
            resp_code, data = self.spectator_mode(player_id, map_id=data)
            query = pack_resp(command, resp_code, self.server_id, data)

        elif command == COMMAND.EXISTING_SHOTS:
            # Usually after connecting to existing game, player sends this command
            data = self.existing_shots(map_id=data)
            query = pack_resp(command, RESP.OK, self.server_id, data)

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
