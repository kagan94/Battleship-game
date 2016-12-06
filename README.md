# Battleship-game

## Already DONE:
* Establishment of sql connection + created basic structure of DB + created models for DB (server)
* register_nickname. If nickname doesn't exist, register it in DB (server)
* create_new_map (server)
* register_hit, but need addition notification for injured ships (server)

## TODO Server:
* add check if someone stayed in this region, if yes hit = 1, otherwise hit = 0 (in register_hit function)

## TODO Client:
* create a local config to store player nickname
* Create OOP structure of client
* Create Async MQ consumer (via Threads with separate connection)

## TODO GUI:
* form to create a nickname
* form to create a new field + size of field
* arrange the ships on the map
* show the map of ships location for player
* show the global map (with other opponents)
* spectator mode


![SQL db scatch](http://clip2net.com/clip/m527982/a642e-clip-43kb.png)
