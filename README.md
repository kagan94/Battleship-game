# Battleship-game

## Already DONE:
* Establishment of sql connection + created basic structure of DB + created models for DB (server)
* register_nickname. If nickname doesn't exist, register it in DB (server)
* create_new_map (server)
* make_hit, but need addition notification for injured ships (server)
* save user nickname locally (client)
* Create OOP structure (client)
* Create Async MQ consumer (via Threads with separate connection)
* Notify admin about joining a new player (server)
* Join existing game (client, server)
* make a shot simple functionality (client, server)
* added parser for server name (server)
* server was rewritten in OOP way
* deleted unnecessary table "invitations" (models, sql)
* add table "server" (db)
* add new server name in db or get existing server_id (server, models)
* rewrite queries with server_id (client, server)
* rewrite queries with chosen server_id (client)
* request to get list of available servers (servers online. function available_servers) from Redis (client)
* delete msg about presence in "servers_online" when server goes off-line in Redis (server)
* possibility to use non-default arguments for Redis, RabbitMQ (client, server)
* added check on accessibility of DB (server)
* added try/except on server to close RabbitMQ connection and delete server presence from Redis
* place player ships randomly (server + on client: command, parse response)
* saved placed ships in DB
* form to create a nickname (GUI)
* list of servers online (GUI)
* fixed bug with putting server name into Redis
* now server_id and server_name are stored as hash map in Redis instead of list as it was earlier
* add check if someone stayed in this region, if yes hit = 1, otherwise hit = 0 (in make_hit function) (server)
* if ship sank, send notification to him
* list of maps done
* notify next player if hit = 0
* form to create a new field + size of field (GUI)
* create random ships locations on the map (GUI)
* show the map of ships location for player (GUI)
* spectator mode (GUI)
* remove double-click (as triger) on the same coordinate on the field that user can click only once on one coordinate (GUI)
* Remove glitch with window freezeing while waiting for the response (Maybe through using separate Thread for GUI) (GUI)


* PLAYER_JOINED_TO_GAME
* YOUR_SHIP_WAS_DAMAGED
* SOMEONE_MADE_SHOT
* notification.SAVE_PLAYER_ID
* notification.GAME_STARTED
* notification.YOU_ARE_KICKED
* notification.YOUR_TURN_TO_MOVE
* notification.GAME_FINISHED
* if ship sank, send notification to damaged player

## TODO Server:
* kick player
* change admin after timeout

## TODO Client:
* Add "KeyboardInterrupt, SystemExit" after connecting GUI

## TODO GUI:

![SQL db scatch](http://clip2net.com/clip/m527982/5b1a1-clip-45kb.png)
