#! /usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *

# Establish connection to our DB
db = MySQLDatabase('battleship', user='root', password='')
db.connect()


class Maps(Model):
    map_id = IntegerField(primary_key=True)
    owner_id = IntegerField()

    class Meta:
        database = db


class Players(Model):
    player_id = IntegerField(primary_key=True)
    nickname = CharField()

    class Meta:
        database = db


class Player_to_map(Model):
    map_id = IntegerField(primary_key=True)
    player_id = IntegerField()

    class Meta:
        database = db


class Ship_placement(Model):
    map_id = IntegerField(primary_key=True)
    player_id = IntegerField()
    raw_start = IntegerField()
    raw_end = IntegerField()
    column_start = IntegerField()
    column_end = IntegerField()
    ship_type = IntegerField()

    class Meta:
        database = db


class Player_hits(Model):
    shot_id = IntegerField(primary_key=True)
    map_id = IntegerField()
    player_id = IntegerField()
    raw = IntegerField()
    column = IntegerField()
    time = TimeField()
    hit = IntegerField()

    class Meta:
        database = db


class Invitations(Model):
    invitation_id = IntegerField(primary_key=True)
    map_id = IntegerField()
    initiator_id = IntegerField()
    invited_player_id = IntegerField()

    class Meta:
        database = db

