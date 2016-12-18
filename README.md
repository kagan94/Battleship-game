# Battleship-game

## Used technologies:
* Redis
* RabbitMQ
* MySQL
* Python 2.7
* Tkinter
* PyGame

# General view of the game
![Game window](http://clip2net.com/clip/m527982/a118a-clip-285kb.png)

# Additional screenshots:
## Register nickname window
![Register nickname](http://clip2net.com/clip/m527982/0aede-clip-36kb.png)

## Choose server window
![Choose server window](http://clip2net.com/clip/m527982/344c8-clip-52kb.png)

## Choose map window
![Choose map window](http://clip2net.com/clip/m527982/841c6-clip-78kb.png)

## Create new map window
![Create new map window](http://clip2net.com/clip/m527982/5af25-clip-44kb.png)

## Main battlefield window
![Main battlefield window](http://clip2net.com/clip/m527982/c6564-clip-148kb.png)

## Main battlefield window with several players
![Main battlefield window with several players](http://clip2net.com/clip/m527982/88b22-clip-247kb.png)

## Structure of database
![structure of database](http://clip2net.com/clip/m527982/cf8d1-clip-47kb.png)


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
* notify next player about his turn
* check whether ship is completely sank, then send argument "completely_sank" to player who made shot
* notify next player if hit = 0
* added formula for limit exceeding
* check on limit exceeding while connecting to the map
* kick player
* add check on spectator mode while joining to game (server, gui)
* mark player that goes into spectator mode (in spectator_mode method. On server)
* add check that there should be at least 2 people on the map before the game can start (start_game method on server)
* send notification when another player disconnected
* restart_game (server, gui)
* change admin when admin quitted
* update turn in DB when admin quitted
* assign new admin when admin quitted
* send notification about game end (when 1 player quitted, and 1 player left)
* send notification about quit of some player to other players on this map
* delete quitted player_name from players list (gui)
* Add notification to other players that this player was kicked (server)
* clean all files
