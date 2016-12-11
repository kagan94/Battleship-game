from redis import ConnectionPool, Redis


# Check that connection with Redis is alive
def check_redis_connection():
    try:
        r_ping = r.ping()
    except:
        r_ping = False
        print "Can't access Redis server, please check connection parameters"
    return r_ping


pool = ConnectionPool(host='localhost', port=6379, db=0)
r = Redis(connection_pool=pool)

if check_redis_connection():
    print 1
    server_name = "serv_1"

    # Show that server online now (in Redis)
    r.sadd("servers_online", server_name)

    # Server goes off-line
    r.srem("servers_online", server_name)

    # Set of servers online (Redis)
    servers_online = r.smembers("servers_online")

    if servers_online:
        # Convert set of servers to list
        servers_online = sorted(list(servers_online))
        servers_online.sort()

        print "Servers online: " + ", ".join(servers_online)
    else:
        print "All server are off-line"

