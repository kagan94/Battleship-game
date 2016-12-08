# Battleship-game

## Already DONE:
* Establishment of sql connection + created basic structure of DB + created models for DB (server)
* register_nickname. If nickname doesn't exist, register it in DB (server)
* create_new_map (server)
* register_hit, but need addition notification for injured ships (server)
* save user nickname locally (client)
* Create OOP structure (client)
* Create Async MQ consumer (via Threads with separate connection)
* Notify admin about joining a new player (server)
* Join existing game (client, server)
* make a shot simple functionallity (client, server)
* added parser for server name (server)
* server was rewritten in OOP way
* deleted unneccessary table "invitations" (models, sql)
* add table "server" (db)
* add new server name in db or get existing server_id (server, models)
* rewrite queries with server_id (client, server)

## TODO Server:
* place player ships randomly
* add check if someone stayed in this region, if yes hit = 1, otherwise hit = 0 (in register_hit function)
* if ship sank, send notification to all players in this game
* notify next player if hit = 0

* (!) delete msg about presence in "servers_online" when server goes off-line (ask Artem)


## TODO Client:
* list of available servers
* rewrite queries with chosen server_id


## TODO GUI:
* form to create a nickname
* form to create a new field + size of field
* create random ships locations on the map
* show the map of ships location for player
* spectator mode


![SQL db scatch](http://clip2net.com/clip/m527982/98592-clip-43kb.png)
