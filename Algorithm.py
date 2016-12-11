import pylab as plt
import math as math
import numpy as np

# Define the problem
players = 3
N  = int(math.ceil(math.sqrt(100*players)))

# Reserve the boards
board = np.zeros((N,N))
print N
#print board

def random_spot(): return np.random.random_integers(0,N-1,2)

#def r_direction(coordinate, ship_type):
#    flag_block = False
    #r_dir = 0

def r_direction(coordinate, ship_type):
    flag_block = False
    #r_dir = 0

    r_dir = np.random.random_integers(0,3)

    #top
    if (r_dir == 0):
        #print "keksik top"
        #print coordinate[1]-ship_type

        if (coordinate[1]-ship_type >= 0):
            coor = coordinate[1]
            for i in range(ship_type):
                if board[coordinate[0],coor] != 0:
                    r_dir = -1
                    break
                else:
                    coor = coor - 1
                    flag_block = False
        else:
            r_dir = -1

        #right
    elif (r_dir == 1):
        #print "keksik right"
        #print coordinate[0] + ship_type < N

        if (coordinate[0]+ship_type<N):
            coor = coordinate[0]
            for i in range(ship_type):
                if board[coor,coordinate[1]] != 0:
                    r_dir = -1
                    break
                else:
                    coor = coor + 1
                    flag_block = False
        else:
            r_dir = -1

    #bottom
    elif (r_dir == 2):
        #print "keksik bot"
        #print coordinate[1]+ship_type<N

        if (coordinate[1]+ship_type<N):
            coor = coordinate[1]
            for i in range(ship_type):
                if board[coordinate[0],coor] != 0:
                    r_dir = -1
                    break
                else:
                    coor = coor + 1
                    flag_block = False
        else:
            r_dir = -1

    #left
    elif (r_dir == 3):
        #print "keksik left"
        #print coordinate[0]-ship_type>=0

        if (coordinate[0]-ship_type>=0):
            coor = coordinate[0]
            for i in range(ship_type):
                if board[coor, coordinate[1]] != 0:
                    r_dir = -1
                    break
                else:
                    coor = coor - 1
                    flag_block = False
        else:
            r_dir = -1

    else:
        r_dir=-1

    return r_dir


def get_ship_type(ship_number):

    if (ship_number < 1 * players):
        return 4
    if (ship_number < 1 * players + 2 * players):
        return 3
    if (ship_number < 1 * players + 2 * players + 3 * players):
        return 2
    if (ship_number < 1 * players + 2 * players + 3 * players + 4 * players):
        return 1

def get_player_number(ship_number):
    p_n = ship_number % players
    return 2 + p_n
'''
def draw(ship_type, player_number, random_spot, r_direction):

        #top
        if (r_direction == 0):

            for k in range(ship_type):

                board[random_spot[0],random_spot[1] - k] = player_number
                if (random_spot[0] + 1<N):
                    board[random_spot[0] + 1, random_spot[1] - k] = 1
                if (random_spot[0] - 1>=0):
                    board[random_spot[0] - 1, random_spot[1] - k] = 1

            board[random_spot[0], random_spot[1] + 1] = 1
            board[random_spot[0] - 1, random_spot[1] + 1] = 1
            board[random_spot[0] + 1, random_spot[1] + 1] = 1
            board[random_spot[0], random_spot[1] - ship_type] = 1
            board[random_spot[0] - 1, random_spot[1] - ship_type] = 1
            board[random_spot[0] + 1, random_spot[1] - ship_type] = 1

        #right
        if (r_direction == 1):

            for k in range(ship_type):

                board[random_spot[0] + k,random_spot[1]] = player_number
                board[random_spot[0] + k, random_spot[1] - 1] = 1
                board[random_spot[0] + k, random_spot[1] + 1] = 1

            board[random_spot[0] - 1, random_spot[1]] = 1
            board[random_spot[0] - 1, random_spot[1] - 1] = 1
            board[random_spot[0] - 1, random_spot[1] + 1] = 1
            board[random_spot[0] + ship_type, random_spot[1]] = 1
            board[random_spot[0] + ship_type, random_spot[1] - 1] = 1
            board[random_spot[0] + ship_type, random_spot[1] + 1] = 1

        #bottom
        if (r_direction == 2):

            for k in range(ship_type):

                board[random_spot[0], random_spot[1] + k] = player_number
                board[random_spot[0] + 1, random_spot[1] + k] = 1
                board[random_spot[0] - 1, random_spot[1] + k] = 1

            board[random_spot[0], random_spot[1] - 1] = 1
            board[random_spot[0] - 1, random_spot[1] - 1] = 1
            board[random_spot[0] + 1, random_spot[1] - 1] = 1
            board[random_spot[0], random_spot[1] + ship_type] = 1
            board[random_spot[0] - 1, random_spot[1] + ship_type] = 1
            board[random_spot[0] + 1, random_spot[1] + ship_type] = 1

        #left
        if (r_direction == 3):

            for k in range(ship_type):

                board[random_spot[0] - k,random_spot[1]] = player_number
                board[random_spot[0] - k, random_spot[1] - 1] = 1
                board[random_spot[0] - k, random_spot[1] + 1] = 1

            board[random_spot[0] + 1, random_spot[1]] = 1
            board[random_spot[0] + 1, random_spot[1] - 1] = 1
            board[random_spot[0] + 1, random_spot[1] + 1] = 1
            board[random_spot[0] - ship_type, random_spot[1]] = 1
            board[random_spot[0] - ship_type, random_spot[1] - 1] = 1
            board[random_spot[0] - ship_type, random_spot[1] + 1] = 1
'''
def draw(ship_type, player_number, random_spot, r_direction):

        #top
        if (r_direction == 0):

            for k in range(ship_type):

                board[random_spot[0],random_spot[1] - k] = player_number
                if (random_spot[0] + 1<N):
                    board[random_spot[0] + 1, random_spot[1] - k] = 1
                if (random_spot[0] - 1>=0):
                    board[random_spot[0] - 1, random_spot[1] - k] = 1

            if (random_spot[1] + 1 < N):
                board[random_spot[0], random_spot[1] + 1] = 1
            if (random_spot[1] + 1 < N) and (random_spot[0] - 1 >= 0):
                board[random_spot[0] - 1, random_spot[1] + 1] = 1
            if (random_spot[0] + 1 < N) and (random_spot[1] + 1 < N):
                board[random_spot[0] + 1, random_spot[1] + 1] = 1
            if (random_spot[1] - ship_type >= 0):
                board[random_spot[0], random_spot[1] - ship_type] = 1
            if (random_spot[0] - 1 >= 0) and (random_spot[1] - ship_type >= 0):
                board[random_spot[0] - 1, random_spot[1] - ship_type] = 1
            if (random_spot[0] + 1 < N) and (random_spot[1] - ship_type >= 0):
                board[random_spot[0] + 1, random_spot[1] - ship_type] = 1

        #right
        if (r_direction == 1):

            for k in range(ship_type):

                board[random_spot[0] + k,random_spot[1]] = player_number
                if (random_spot[1] - 1>=0):
                    board[random_spot[0] + k, random_spot[1] - 1] = 1
                if (random_spot[1] + 1<N):
                    board[random_spot[0] + k, random_spot[1] + 1] = 1

            if (random_spot[0] - 1>=0):
                board[random_spot[0] - 1, random_spot[1]] = 1
            if (random_spot[0] - 1>=0) and (random_spot[1] - 1>=0):
                board[random_spot[0] - 1, random_spot[1] - 1] = 1
            if (random_spot[0] - 1>=0) and (random_spot[1] + 1<N):
                board[random_spot[0] - 1, random_spot[1] + 1] = 1
            if (random_spot[1] + ship_type<N):
                board[random_spot[0] + ship_type, random_spot[1]] = 1
            if (random_spot[1] - 1>=0) and (random_spot[0] + ship_type<N):
                board[random_spot[0] + ship_type, random_spot[1] - 1] = 1
            if (random_spot[1] + 1<N) and (random_spot[0] + ship_type<N):
                board[random_spot[0] + ship_type, random_spot[1] + 1] = 1

        #bottom
        if (r_direction == 2):

            for k in range(ship_type):

                board[random_spot[0],random_spot[1] + k] = player_number
                if (random_spot[0] + 1<N):
                    board[random_spot[0] + 1, random_spot[1] + k] = 1
                if (random_spot[0] - 1>=0):
                    board[random_spot[0] - 1, random_spot[1] + k] = 1

            if (random_spot[1] - 1 >= 0):
                board[random_spot[0], random_spot[1] - 1] = 1
            if (random_spot[0] - 1 >= 0) and (random_spot[1] - 1 >= 0):
                board[random_spot[0] - 1, random_spot[1] - 1] = 1
            if (random_spot[1] - 1 >= 0) and (random_spot[0] + 1 < N):
                board[random_spot[0] + 1, random_spot[1] - 1] = 1
            if (random_spot[1] + ship_type < N):
                board[random_spot[0], random_spot[1] + ship_type] = 1
            if (random_spot[0] - 1 >= 0) and (random_spot[1] + ship_type < N):
                board[random_spot[0] - 1, random_spot[1] + ship_type] = 1
            if (random_spot[0] + 1 < N) and (random_spot[1] + ship_type < N):
                board[random_spot[0] + 1, random_spot[1] + ship_type] = 1

        #left
        if (r_direction == 3):

            for k in range(ship_type):

                board[random_spot[0] - k,random_spot[1]] = player_number
                if (random_spot[1] - 1>=0):
                    board[random_spot[0] - k, random_spot[1] - 1] = 1
                if (random_spot[1] + 1<N):
                    board[random_spot[0] - k, random_spot[1] + 1] = 1

            if (random_spot[0] + 1 < N):
                board[random_spot[0] + 1, random_spot[1]] = 1
            if (random_spot[0] + 1 < N) and (random_spot[1] - 1 >= 0):
                board[random_spot[0] + 1, random_spot[1] - 1] = 1
            if (random_spot[0] + 1 < N) and (random_spot[1] + 1 < N):
                board[random_spot[0] + 1, random_spot[1] + 1] = 1
            if (random_spot[0] - ship_type >= 0):
                board[random_spot[0] - ship_type, random_spot[1]] = 1
            if (random_spot[1] - 1 >= 0) and (random_spot[0] - ship_type >=0 ):
                board[random_spot[0] - ship_type, random_spot[1] - 1] = 1
            if (random_spot[1] + 1 < N ) and (random_spot[0] - ship_type >= 0):
                board[random_spot[0] - ship_type, random_spot[1] + 1] = 1


for x in range (10 * players):
    direction = -1
    #print '***'
    #print board
    ship_type =get_ship_type(x)
    player_number=get_player_number(x)
    #rand_point =random_spot()
    #direction=r_direction(rand_point,ship_type)
    while (direction == -1):
        rand_point = random_spot()
        direction = r_direction(rand_point, ship_type)
    draw(ship_type, player_number, rand_point, direction)


print board


plt.matshow(board)
plt.show()