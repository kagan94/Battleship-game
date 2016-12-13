#! /usr/bin/env python
# -*- coding: utf-8 -*-

# from playhouse.pool import PooledMySQLDatabase
from peewee import *
import datetime

# Establish connection to our DB
db = MySQLDatabase('battleship', user='root', password='')
db.connect()

# db = PooledMySQLDatabase('battleship',**{
#             "user": "root", "passwd": "",
#             "max_connections":20, "stale_timeout":None,
#             "threadlocals":True
#         })


class BaseModel(Model):
    class Meta:
        database = db


class Player(BaseModel):
    player_id = IntegerField(primary_key=True)
    nickname = CharField()

    def __str__(self):
        return "Player's id:%s, nickname:%s" % (self.id, self.nickname)


class Server(BaseModel):
    server_id = IntegerField(primary_key=True)
    name = CharField()

    def __str__(self):
        return "Server's id:%s, name:%s" % (self.id, self.name)


class Map(BaseModel):
    map_id = IntegerField(primary_key=True)
    server = ForeignKeyField(Server)
    owner = ForeignKeyField(Player)
    name = CharField()
    rows = IntegerField()
    columns = IntegerField()
    game_started = IntegerField()

    def __str__(self):
        return "Map_id:%s, server_name:%s, owner:%s, map_name:%s, rows:%s, columns:%s, game_started: %s"\
               % (self.map_id, self.server.name, self.owner,
                  self.name, self.rows, self.columns, self.game_started)


class Player_to_map(BaseModel):
    map = ForeignKeyField(Map)
    player = ForeignKeyField(Player, related_name="maps")  # user's playing on these maps
    time_connected = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return "Map_id:%s, player:%s, time_connected:%s" % (self.map_id, self.player.nickname, self.time_connected)

    class Meta:
        primary_key = CompositeKey('map', 'player')


class Ship_to_map(BaseModel):
    location_id = IntegerField(primary_key=True)
    map = ForeignKeyField(Map)
    player = ForeignKeyField(Player)
    row_start = IntegerField()
    row_end = IntegerField()
    column_start = IntegerField()
    column_end = IntegerField()
    ship_type = IntegerField()

    def __str__(self):
        return "Location_id:%s, Map_id:%s, player:%s, row_start:%s, row_end:%s, column_start:%s, " \
               "column_end:%s, ship_type:%s"\
               %(self.location_id, self.map_id, self.player.nickname, self.row_start, self.row_end,
                 self.column_start, self.column_end, self.ship_type)

    # class Meta:
    #     primary_key = CompositeKey('', 'map', 'player')


class Player_hits(BaseModel):
    shot_id = IntegerField(primary_key=True)
    map = ForeignKeyField(Map)
    player = ForeignKeyField(Player)
    row = IntegerField()
    column = IntegerField()
    time = DateTimeField(default=datetime.datetime.now)
    hit = IntegerField()

    def __str__(self):
        return "shot_id:%s, map_id:%s, player:%s, row:%s, column:%s, time:%s, hit:%s" \
               % (self.shot_id, self.map_id, self.player.nickname, self.row, self.column,
                  self.time, self.hit)


# class Invitation(BaseModel):
#     invitation_id = IntegerField()
#     map = ForeignKeyField(Map)
#     initiator = ForeignKeyField(Player, related_name='initiator')
#     invited_player = ForeignKeyField(Player, related_name='invited_player')
#
#     def __str__(self):
#         return "invitation_id:%s, map_id:%s, initiator:%s, invited_player:%s" \
#                % (self.invitation_id, self.map_id, self.initiator.nickname, self.invited_player.nickname)
#
#     class Meta:
#         primary_key = CompositeKey('invitation', 'map', 'initiator', 'invited_player')
