import time
import pygame
import tkMessageBox
import Queue

from Tkinter import *
from ScrolledText import *
from threading import Thread, Lock
from client import lock

# Local import
from common import *

######################
# Globals for Pygame
# This sets the WIDTH and HEIGHT of each grid location
HEIGHT = 12
WIDTH = 12

# This sets the margin between each cell
MARGIN = 2

# Define some general colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class GUI(object):
    nickname_root = None
    server_root = None
    select_map_root = None
    create_new_map_root = None
    players_root = None

    my_turn_to_move = False
    selected_player, selected_player_id = None, None

    pygame_done = True
    players_on_map = {}
    players_l = None  # Players list

    def __init__(self):
        # Queue to collect and proceed the tasks from server
        self.tasks = Queue.Queue()

        # Queue to collect and proceed the tasks in pygame
        # self.pygame_tasks = Queue.Queue()
        # self.pygame_lock = Lock()

        self.client = None
        self.root = None
        self.frame = None

        self.popup_msg = None

        self.selected_server = None
        self.selected_server_id = None

        self.maps = {}
        self.selected_map = None
        self.selected_map_id = None
        # self.selected_map_size = None

        self.maps_list = None
        self.connect_to_map_b = None
        self.create_new_game_b = None

        self.field_size = None

    def notification_window(self):
        self.root = Tk()
        self.root.title("Notification Center")

        frame = Frame(self.root)
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.pack(pady=10, padx=10)

        notification = Label(self.root, text=">> Notification Center <<")
        notification.pack()

        # Notification area
        self.notifications = ScrolledText(self.root, width=30, height=20, state=NORMAL)
        self.notifications.pack()

        # Each 10 ms check whether client received something or not
        # print self.client.resp
        # self.add_notification(str(i))

        while True:
            # print self.tasks._qsize()
            try:
                task = self.tasks.get(False)
                # print task

            # Handle empty queue here
            except Queue.Empty:
                pass
            else:
                # Handle task here and call q.task_done()
                self.process_task(task)
                self.tasks.task_done()

            # try:
            # win = Tk()

            try:
                self.root.update_idletasks()
                self.root.update()

            # Catch error "can't invoke "update" command:
            # application has been destroyed
            except TclError, KeyboardInterrupt:
                return
            except AttributeError:
                print "Error: root can't be NoneType"
                break

            time.sleep(0.1)

            # except:
            #     .update_idletasks()
            #     win2.update()
            #     time.sleep(0.1)


            # if self.client.resp is None:
            #     # print "window's alive"
            #     try:
            #         self.root.after(10, self.check_resp)  # timeout 10 ms
            #     # If app was already destroyed
            #     except:
            #         pass
            # else:
            #     self.root.destroy()
            #     print "window is destroying"
            #     # self.destoy_root()

    def nickname_window(self):
        self.nickname_root = Tk()
        self.nickname_root.title("Enter a nickname")

        self.frame = Frame(self.nickname_root)
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack(pady=10, padx=10)

        self.name = Label(self.nickname_root, text="Enter a nickname")
        self.name.pack()

        self.nickname = StringVar()
        self.e = Entry(self.nickname_root, textvariable=self.nickname)
        self.e.pack()

        self.check_nick_button = Button(self.nickname_root, text="Choose", command=self.on_nickname_submit)
        self.check_nick_button.pack()

        # with lock:
        #     self.tasks.put("launch_nickname_window")

        # self.root.mainloop()

    def choose_server_window(self):
        # Destroy previous window
        self.destroy_previous_root()

        # Update server_id to avoid conflicts in queries
        self.client.selected_server_id = None
        self.selected_server = None

        self.server_root = Tk()
        self.server_root.title("Choose a server")

        self.frame = Frame(self.server_root)
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack(pady=10, padx=10)

        self.server = Label(self.server_root, text="Choose a server")
        self.server.pack()

        # Servers on-line list
        self.servers_list = Listbox(self.server_root, height=12)
        self.servers_list.pack()
        self.servers_list.bind('<<ListboxSelect>>', self.on_server_selection)

        # Join server button
        self.join_server_b = Button(self.server_root, text="Connect", command=self.choose_map_window, state=DISABLED)
        self.join_server_b.pack()

        # if self.choose_map_window is None:
        #     self.choose_map_window()

        # Show client which servers are on-line (get from Redis)
        self.servers_online = self.client.available_servers()

        for server_name in self.servers_online.values():
            self.servers_list.insert(END, server_name + "\n")

    def choose_map_window(self):
        ''' In this window, player can either create a new game or join existing game '''

        # Destroy previous window
        self.destroy_previous_root()

        self.selected_map = None

        self.select_map_root = Tk()
        self.select_map_root.title("Choose a map")

        self.frame = Frame(self.select_map_root)
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack(pady=10, padx=10)

        self.game_l = Label(self.select_map_root, text="Choose a map")
        self.game_l.pack()

        # Available maps
        self.maps_list = Listbox(self.select_map_root, height=12)
        self.maps_list.pack()
        self.maps_list.bind('<<ListboxSelect>>', self.on_game_selection)

        # Join server button
        self.connect_to_map_b = Button(self.select_map_root, text="Connect to selected map",
                                       command=self.on_connect_to_map, state=DISABLED)
        # command=self.on_connect_to_map, state=DISABLED)
        self.connect_to_map_b.pack()

        self.create_new_game_b = Button(self.select_map_root, text="Create new map",
                                        command=self.create_new_map_window)
        self.create_new_game_b.pack()

        go_to_servers_lobby_b = Button(self.select_map_root, text="Go to servers lobby",
                                       command=self.choose_server_window)
        go_to_servers_lobby_b.pack()

        # Get available servers on this server
        self.client.available_maps()

    def create_new_map_window(self):
        ''' Player decided to create new map window '''

        # Destroy previous window
        self.destroy_previous_root()

        self.create_new_map_root = Tk()
        self.create_new_map_root.title("Create new game")

        self.gamelistframe = Frame(self.create_new_map_root)
        self.gamelistframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.gamelistframe.columnconfigure(0, weight=1)
        self.gamelistframe.rowconfigure(0, weight=1)
        self.gamelistframe.pack(pady=10, padx=10)

        self.field = Label(self.create_new_map_root, text="Select a size of the field")
        self.field.pack()

        self.size = 20

        choices = {
            'S',
            'M',
            'L'
        }

        self.field_size_option = StringVar(self.create_new_map_root)
        self.option = OptionMenu(self.gamelistframe, self.field_size_option, *choices)

        # Set default field size to "Small"
        self.field_size_option.set('S')

        self.option.grid(row=1, column=1)

        def change_size(*args):
            global size
            choice = self.field_size_option.get()

            if choice == "S":
                self.field_size = 20
            elif choice == "M":
                self.field_size = 40
            elif choice == "L":
                self.field_size = 50

        # trace the change of var
        self.field_size_option.trace('w', change_size)

        label = Label(self.nickname_root, text="Enter a map name")
        label.pack()

        self.new_map_name = StringVar()
        self.new_map_name_t = Entry(self.create_new_map_root, textvariable=self.new_map_name)
        self.new_map_name_t.pack()

        self.create_map_b = Button(self.create_new_map_root, text="Create map", command=self.on_create_map)
        self.create_map_b.pack()

        self.go_to_maps_b = Button(self.create_new_map_root, text="<< Go back to maps", command=self.choose_map_window)
        self.go_to_maps_b.pack()

    def players_on_map_window(self):
        ''' Window with current players on this map '''
        self.players_root = Tk()
        self.players_root.title("Players Online")

        frame = Frame(self.players_root)
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.pack(pady=10, padx=10)

        label = Label(self.players_root, text="Players Online")
        label.pack()

        # List of players on this map
        self.players_l = Listbox(self.players_root, width=12, height=15)
        self.players_l.pack()
        self.players_l.bind('<<ListboxSelect>>', self.on_player_selection)

        # "Start game" button
        self.start_game_b = Button(self.players_root, state=DISABLED, text="Start game", command=self.on_start_game)
        self.start_game_b.pack()

        self.place_ships_b = Button(self.players_root, state=DISABLED, text="Place ships", command=self.on_place_ships)
        self.place_ships_b.pack()

        # Spectator mode
        self.spectator_mode_b = Button(self.players_root, state=DISABLED, text="Spectator mode",
                                       command=self.client.spectator_mode)
        self.spectator_mode_b.pack(padx=5, pady=5)

        # Kick player
        self.kick_player_b = Button(self.players_root, state=DISABLED, text="Kick selected player",
                                    command=self.on_kick_player)
        self.kick_player_b.pack(padx=5, pady=5)

        # Restart game button (can be pressed only after game finished)
        self.restart_game_b = Button(self.players_root, state=DISABLED, text="Restart game",
                                     command=self.on_restart_game)
        self.restart_game_b.pack()

        # Disconnect from the game
        self.disconnect_b = Button(self.players_root, text="Disconnect", command=self.on_disconnect)
        self.disconnect_b.pack()

        # Quit
        self.quit_b = Button(self.players_root, text="Quit from the game", command=self.on_quit)
        self.quit_b.pack()

    def run_game(self):
        # Destroy previous window
        self.destroy_previous_root()

        # This var is responsible to make a move on the battlefield
        self.my_turn_to_move = False

        # Create new thread to draw field
        field_t = Thread(target=self.draw_field)
        field_t.setDaemon(True)
        field_t.start()

        self.players_on_map_window()

    def draw_field(self):
        '''' Here we draw our field and parse changes '''

        # If the map_size is unknown, then exit
        if self.field_size is None:
            return

        field_name = self.selected_map
        self.my_ships_locations = []
        self.players_on_map = dict()  # key - player_id, value - dict("name":nickname, "disconnected":val)

        ########
        # Request to get all players on the map and player's ships
        with lock:
            self.client.my_ships_on_map()
            self.client.players_on_map()
        ########

        # Save my presence on this map
        self.players_on_map[self.client.my_player_id] = {
            "name": self.client.nickname,
            "disconnected": "0"
        }

        def get_colors():
            ''' Return list with 15 colors (as tuples) '''
            RED = (255, 0, 0)
            YELLOW = (255, 255, 0)
            BLUE = (0, 0, 255)
            CYAN = (0, 255, 255)
            MAGENTA = (255, 0, 255)
            MAROON = (128, 0, 0)
            PURPLE = (128, 0, 128)
            ORANGE = (255, 165, 0)
            CHOCOLATE = (210, 105, 30)
            LIGHT_GRAY = (119, 136, 153)
            PINK = (255, 192, 203)
            OLIVE = (128, 128, 0)
            TEAL = (0, 128, 128)
            DARK_GREEN = (0, 128, 0)
            MIDNIGHT_BLUE = (25, 25, 112)
            return [RED, YELLOW, BLUE, CYAN, MAGENTA, MAROON, PURPLE,
                    ORANGE, CHOCOLATE, LIGHT_GRAY, PINK, OLIVE,
                    TEAL, DARK_GREEN, MIDNIGHT_BLUE]

        # Pre-defined dict with 15 possible colors
        self.possible_colors = get_colors()

        # To store colors for different ships (format key - player_id, val - color)
        self.players_colors = {}

        ##############
        # Colors for different types of shots
        PAPAYA_WHIP = (255, 239, 213)
        INDIAN_RED = (205, 92, 92)
        LIME_GREEN = (50, 205, 50)

        self.shots_colors = {
            -10: INDIAN_RED,  # My ship was damaged
            -11: LIME_GREEN,  # My hit was successful
            -12: PAPAYA_WHIP,  # I made shot, but I missed
        }

        ##############

        # By default color for my ships is GREEN
        GREEN = (0, 255, 0)
        self.players_colors[self.client.my_player_id] = GREEN

        # Create a 2 dimensional array. A two dimensional
        # array is simply a list of lists.
        self.grid = []

        self.size = self.field_size

        for row in range(self.size):
            # Add an empty array that will hold each cell
            # in this row
            self.grid.append([])
            for column in range(self.size):
                self.grid[row].append(0)  # Append a cell

        # Set row 1, cell 5 to one.
        # (Remember rows and column numbers start at zero.)
        # self.grid[1][5] = 1

        # Initialize pygame
        pygame.init()

        # Set the HEIGHT and WIDTH of the screen
        self.max_size = (WIDTH + MARGIN) * self.size + MARGIN
        self.WINDOW_SIZE = [self.max_size, self.max_size]
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)

        # Set title of screen
        pygame.display.set_caption("Battlefield: %s" % field_name)

        # Loop until the user clicks the close button.
        self.pygame_done = False

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        def draw_dash(i, j):
            # print i, j
            # x1, x2 = 20, 20 + MARGIN + WIDTH
            # y1, y2 = 120, 120
            # i, j = 19, 19

            # x1 = (MARGIN + WIDTH) * j
            # x2 = (MARGIN + WIDTH) * j + MARGIN + WIDTH
            # y1 = y2 = (MARGIN + HEIGHT) * i - ((MARGIN + HEIGHT) / 2)

            x1 = (MARGIN + WIDTH) * i
            x2 = (MARGIN + WIDTH) * i + MARGIN + WIDTH
            y1 = (MARGIN + HEIGHT) * j + (MARGIN + HEIGHT) / 2
            y2 = (MARGIN + HEIGHT) * j + (MARGIN + HEIGHT) / 2

            # if y2 > self.maxx:
            #     self.maxx = y2
            #     print x1, x2, "_____"

            # x1, x2, y2 = 0, 14, 275
            # y1 = y2

            # print x1, x2, y2, MARGIN + WIDTH, y2 >= self.max_size, x1 >= self.max_size, x2 >= self.max_size,
            pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2), 3)

        def draw_cross(i, j):
            x1 = (MARGIN + WIDTH) * i
            x2 = (MARGIN + WIDTH) * i + MARGIN + WIDTH
            y1 = (MARGIN + HEIGHT) * j
            y2 = (MARGIN + HEIGHT) * j + MARGIN + HEIGHT

            pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2), 3)
            pygame.draw.line(self.screen, BLACK, (x2, y1), (x1, y2), 3)

            # print x1, x2, y1, y2, "<<<<<<<<<<<<<<<<<<<<<<<<<<<"

        # -------- Main Program Loop -----------
        while not self.pygame_done:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self.pygame_done = True  # Flag that we are done so we exit this loop

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # and self.my_turn_to_move
                    # User clicks the mouse. Get the position
                    pos = pygame.mouse.get_pos()

                    # Change the x/y screen coordinates to grid coordinates
                    target_column = pos[0] // (WIDTH + MARGIN)
                    target_row = pos[1] // (HEIGHT + MARGIN)

                    try:
                        cell = self.grid[target_row][target_column]
                    except IndexError:
                        break

                    # Request to register shot
                    # Here we need to check that player didn't shot in one cell twice

                    # print cell, self.players_colors.keys(), self.shots_colors.keys()

                    if cell not in self.players_colors.keys() \
                            and cell not in self.shots_colors.keys() \
                            and self.my_turn_to_move:
                        # Change state for my turn, until something will arrive from the server
                        with lock:
                            self.my_turn_to_move = False

                        self.client.make_shot(target_row, target_column)
                    print("Click ", pos, "Grid coordinates: ", target_row, target_column)

            # Set the screen background
            self.screen.fill(BLACK)

            # try:
            # Draw the grid
            for row in range(self.size):
                for column in range(self.size):
                    color = WHITE

                    key = self.grid[row][column]

                    # print self.players_colors
                    # My ships
                    # if key == -1:
                    # color = self.players_colors[self.client.my_player_id]
                    # color = BLACK

                    # In this case 'key" = player_id
                    if key in self.players_colors.keys():
                        color = self.players_colors[key]

                    damaged_player_id = str((-1) * int(key))

                    # print self.client.my_player_id in self.players_colors.keys()
                    if damaged_player_id in self.players_on_map.keys():
                        # print self.players_colors
                        color = self.players_colors[damaged_player_id]

                    pygame.draw.rect(self.screen,
                                     color,
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])

                    # For cases:
                    # - My ship was damaged
                    # - My hit was successful
                    if key in [-10, -11] or damaged_player_id in self.players_on_map.keys():
                        # draw_dash(column, row)
                        draw_cross(column, row)

                    # Someone made a shot, but missed
                    elif key == -12:
                        draw_dash(column, row)
            # except IndexError:
            #     pass

            # Limit to 60 frames per second
            clock.tick(60)

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

        # Be IDLE friendly. If you forget this line, the program will 'hang'
        # on exit.
        pygame.quit()

    def place_ships_on_map(self):
        ''' Place ships on the pygame map (info about ships coords is from the server) '''

        # ships_locations = [(x1, x2, y1, y2, ship_size), ...]
        with lock:
            try:
                for x1, x2, y1, y2, ship_size in self.my_ships_locations:
                    x1, x2, y1, y2 = map(int, [x1, x2, y1, y2])

                    for i in range(x1, x2 + 1):
                        for j in range(y1, y2 + 1):
                            # Specify the color of my ships
                            self.grid[i][j] = self.client.my_player_id
                            # print x1, x2, y1, y2

            except AttributeError:
                pass

    def go_to_spectator_mode(self, info):
        ''' Spectator mode allows to see all ships of all players '''

        # Parse (player_id, x1, x2, y1, y2, and ship size) as tuple
        with lock:
            for k in range(0, len(info), 6):
                # print "dsadas", info[k:k+6]
                player_id = info[k]
                x1, x2, y1, y2 = map(int, [info[k + 1], info[k + 2], info[k + 3], info[k + 4]])
                ship_size = info[k + 5]

                # If player's ships don't have color, generate a new color
                if player_id not in self.players_colors.keys():
                    color = self.possible_colors.pop(0)
                    self.players_colors[player_id] = color

                # Place these ships on the map
                for i in range(x1, x2 + 1):
                    for j in range(y1, y2 + 1):
                        self.grid[i][j] = player_id

    def mark_cell(self, target_row, target_column, hit_successful, damaged_player_id=None):
        '''
        Mark ceil after shot or someone made a damage for my ship

        :param target_row:
        :param target_column:
        :param hit_successful: (str)
        :param my_ship_was_damaged: (bool)
        '''
        i, j = int(target_row), int(target_column)

        # TODO: Add color for damaged_player_id (in case of hit_successful)

        with lock:
            if hit_successful == "1" and damaged_player_id is not None:
                # print "damaged_player_id", damaged_player_id

                self.grid[i][j] = (-1) * int(damaged_player_id)

            elif hit_successful == "1":
                self.grid[i][j] = -11

            # self my_ship_was_damaged

            # Depending on whether the hit was successful or not, mark cell differently
            # if my_ship_was_damaged is None:
            #     self.grid[i][j] = -10
            #
            #     print "damaged_player_id %s, type(%s)" % (damaged_player_id, type(damaged_player_id))
            #     if damaged_player_id is not None:
            #         print 111111111, (-1) * int(damaged_player_id), str(int(damaged_player_id)) in self.players_colors.keys()
            #         self.grid[i][j] = (-1) * int(damaged_player_id)
            #
            # # My hit was successful, update the battlefield
            # elif hit_successful == "1":
            #     self.grid[i][j] = -11

            # I made shot, but I missed
            else:
                self.grid[i][j] = -12

    #################
    # Handlers ============================================================================
    #################
    def on_nickname_submit(self):
        nickname = self.nickname.get()

        # Nickname received
        if len(nickname):
            # Block the button, until we receive the answer
            self.check_nick_button.config(state=DISABLED)

            # Put msg into MQ to register msg and wait until the server will register our nickname
            self.client.register_nickname(nickname)
        else:
            tkMessageBox.showinfo("Error", "Please enter nickname")

    def on_server_selection(self, event):
        widget = self.servers_list

        try:
            index = int(widget.curselection()[0])
            selected_server = widget.get(index).strip()
        except:
            selected_server = None

        # Only 1 click to connect to particular server is allowed
        if selected_server is not None and (self.selected_server != selected_server):
            # Unblock "join server" button
            self.join_server_b.config(state=NORMAL)

            # Get selected server_id by selected server name
            self.selected_server_id = self.servers_online.keys()[
                self.servers_online.values().index(selected_server)]
            self.client.selected_server_id = self.selected_server_id

            # Save chosen server name
            self.selected_server = selected_server

            # print self.selected_server, self.selected_server_id

    def on_game_selection(self, event):
        self.connect_to_map_b.config(state=NORMAL)

        widget = self.maps_list
        try:
            index = int(widget.curselection()[0])
            selected_map = widget.get(index).strip()
        except:
            selected_map = None

        # Only 1 click to connect to particular server is allowed
        if selected_map is not None \
                and (self.selected_map != selected_map) \
                and self.connect_to_map_b.cget("state") == NORMAL:

            # Save selected map name
            self.selected_map = selected_map

            # Get selected map_id by selected map name
            for map_id, map_params in self.maps.items():
                if map_params["name"] == self.selected_map:
                    self.selected_map_id = map_id
                    self.field_size = int(map_params["size"])  # list [rows, columns]
                    break

            # self.client.selected_map_id = self.selected_map_id

            print self.selected_map, self.selected_map_id

    def on_player_selection(self, event):
        widget = self.players_l  # list of players

        try:
            index = int(widget.curselection()[0])
            selected_player = widget.get(index).strip()
        except:
            selected_player = None

        # Save selected nickname
        if selected_player is not None and (self.selected_player != selected_player):
            self.selected_player = selected_player

            # params contains "name" and "disconnected" (0 or 1)
            for player_id, params in self.players_on_map.items():
                if params["name"] == selected_player:
                    self.selected_player_id = player_id
                    break

    def on_connect_to_server(self):
        ''' When player click button "Connect to selected map" '''
        if self.selected_server:
            self.join_server_b.config(state=DISABLED)

            # TODO: Request to connect to the map
            self.choose_map_window()

    def on_connect_to_map(self):
        ''' When player click button "Connect to selected map" '''

        if self.selected_map:
            self.connect_to_map_b.config(state=DISABLED)
            self.create_new_game_b.config(state=DISABLED)

            print "Waiting for response from server"

            self.client.join_game()
            # TODO: Request to connect to the map

    def on_create_map(self):
        # Send request to create new map
        if self.new_map_name.get():
            # Disable the button create new map with parameters
            # until we will receive response from server
            self.create_map_b.config(state=DISABLED)
            self.go_to_maps_b.config(state=DISABLED)

            # Save map name
            self.selected_map = self.new_map_name.get()

            # Request to create new game on server
            self.client.create_new_game(game_name=self.new_map_name.get(), field_size=self.field_size)
        else:
            tkMessageBox.showinfo("Error", "Please enter map name")

    def on_place_ships(self):
        ''' Player wants to place his ships '''
        self.place_ships_b.config(state=DISABLED)

        # Request to place ships
        self.client.place_ships()

    def on_kick_player(self):
        ''' Trigger client to send request with command "Kick selected palyer" '''
        if self.selected_player_id:
            self.kick_player_b.config(state=DISABLED)

            self.client.kick_player(player_id=self.selected_player_id)

            # TODO: Get selected player name and send request to kick it

    def on_start_game(self):
        ''' Trigger client to send request with command "Start game" '''
        # Set button state to disable, until we will receive the response
        self.start_game_b.config(state=DISABLED)

        self.client.start_game()

    def on_restart_game(self):
        ''' Trigger client to send request with command "Restart game" '''
        # Set button state to disable, until we will receive the response
        self.restart_game_b.config(state=DISABLED)

        self.client.restart_game()

    def on_disconnect(self):
        ''' Player wants to disconnect from the game. Should redirect to maps '''
        self.place_ships_b.config(state=DISABLED)
        self.spectator_mode_b.config(state=DISABLED)
        self.kick_player_b.config(state=DISABLED)
        self.start_game_b.config(state=DISABLED)
        self.restart_game_b.config(state=DISABLED)

        self.client.disconnect_from_game()

    def on_quit(self):
        ''' Player wants to quit from the game. Should redirect to maps '''
        with lock:
            self.pygame_done = True

        # self.destroy_previous_root()
        self.choose_map_window()

    #############################################
    # Other methods
    #############################################
    def destoy_root(self):
        # Destroy previous window
        if self.root:
            self.root.destroy()
            self.root = None

        self.client.resp = None

    def unfreeze_connect_to_map_buttons(self):
        # print self.connect_to_map_b, type(self.connect_to_map_b)

        # Unblock buttons to create or join to the server
        if self.connect_to_map_b and self.create_new_game_b:
            self.connect_to_map_b.config(state=NORMAL)
            self.create_new_game_b.config(state=NORMAL)

    def add_notification(self, msg):
        msg = "> " + str(msg) + "\n"
        self.notifications.insert(0.0, msg)

        # def show_popup(self, msg):
        #     print msg
        # tkMessageBox.showinfo("Notification", msg)
        # self.popup_msg = None
        # self.popup_msg = msg

    def update_maps_list(self):
        # Update list of maps inside window choose maps
        # self.maps is a dict[map_id] = {"name":map_name, "size": field_size]

        # print self.maps_list

        if self.maps_list:
            # delete all previous items from previous list
            self.maps_list.delete(0, END)

            try:
                pos = 0
                for map_params in self.maps.values():
                    self.maps_list.insert(END, map_params["name"] + "\n")

                    self.mark_map_in_list(
                        map_name=map_params["name"], game_started=map_params["game_started"], pos_in_list=pos)

                    pos += 1

            except TclError as e:
                print "Error in update maps list"
                return

    def mark_map_in_list(self, map_name, game_started, pos_in_list=None):
        '''
        Mark map in list depending on its current status

        :param map_name: (str)
        :param game_started: (str) 0 - no, 1 - yes, 2 - game finished
        :param pos: (int) (position of map in the list)
        '''

        # print "map_name", map_name, game_started, pos_in_list
        if pos_in_list is None:
            all_maps = self.maps_list.get(0, END)
            pos_in_list = -1

            # Find player in list by his nickname
            for i, el in enumerate(all_maps):
                if el == map_name:
                    pos_in_list = i
                    break

        # If player was found, then  mark him
        if pos_in_list != -1:
            # print 11, game_started == "0"
            if game_started == "0":
                self.maps_list.itemconfig(pos_in_list, bg='green')

            elif game_started == "1":
                self.maps_list.itemconfig(pos_in_list, bg='red')

            elif game_started == "2":
                self.maps_list.itemconfig(pos_in_list, bg='gray')

    def destroy_previous_root(self):
        ''' Destroy previous window '''

        # Destroy window to enter nickname
        if self.nickname_root:
            self.nickname_root.destroy()
            self.nickname_root = None

        # Destroy window to choose server
        if self.server_root:
            self.server_root.destroy()
            self.server_root = None

        # Destroy window to choose map
        if self.select_map_root:
            self.select_map_root.destroy()
            self.select_map_root = None

        # Destroy window to create new game (with parameters)
        if self.create_new_map_root:
            self.create_new_map_root.destroy()
            self.create_new_map_root = None

        # Destroy window with players
        if self.players_root:
            self.players_root.destroy()
            self.players_root = None

    def mark_player_in_list(self, player_nickname, kicked=False, disconnected=False, turn=False):
        '''
            Here we mark player with specific color depending on player state.
            If kicked - mark red, if disconnected - mark gray.
            If it's player_nickname turn, then mark his nickname in list with green color.
        '''

        all_players = self.players_l.get(0, END)
        pos_in_list = -1

        # Find player in list by his nickname
        for i, el in enumerate(all_players):
            if el == player_nickname:
                pos_in_list = i
                break

        # If player was found, then  mark him
        if pos_in_list != -1:
            if kicked:
                self.players_l.itemconfig(pos_in_list, bg='red')

            elif disconnected:
                self.players_l.itemconfig(pos_in_list, bg='gray')

            # If it's player's turn - mark him with green
            elif turn:
                self.players_l.itemconfig(pos_in_list, bg='green')

            # If it's player's turn - mark him with default color
            elif turn == False:
                self.players_l.itemconfig(pos_in_list, bg=None)

    def remove_player_from_players_list(self, player_nickname):
        '''
            Here we iterate over the list of current of players on the map,
            to find and remove requested player
        '''

        all_players = self.players_l.get(0, END)
        pos_in_list = -1

        for i, el in enumerate(all_players):
            if el == player_nickname:
                pos_in_list = i
                break

        if pos_in_list != -1:
            self.players_l.delete(pos_in_list)

    ####################
    # Important function to process responses from servers
    ####################
    def process_task(self, task):
        ''' Handler to receive response on request reg_me '''
        command, resp_code, server_id, data = parse_response(task)

        # print command, resp_code, server_id, data

        print ">> Received resp(%s) on command: %s, server(%s)" \
              % (error_code_to_string(resp_code), command_to_str(command), server_id)

        # print task

        # +
        if command == COMMAND.LIST_OF_MAPS:
            maps_data = parse_data(data)
            self.maps = {}

            if len(maps_data) == 1 and maps_data[0] == "":
                self.add_notification("No available maps online")

            else:
                # with lock:
                # Decompress maps (map_id, map_name, field size) to dict[map_id] = [params]
                for i in range(0, len(maps_data), 4):
                    map_id = maps_data[i]
                    map_name, field_size = maps_data[i + 1], maps_data[i + 2]
                    game_started = maps_data[i + 3]

                    self.maps[map_id] = {
                        "name": map_name,
                        "size": field_size,
                        "game_started": game_started
                    }

                self.update_maps_list()
                self.add_notification("List with maps updated successfully")

        # +
        elif command == COMMAND.CREATE_NEW_GAME:
            map_id, map_name, map_size = parse_data(data)

            if resp_code == RESP.OK:
                # Start the game and open new field
                self.run_game()

                self.maps[map_id] = {
                    "name": map_name,
                    "size": map_size
                }

                # Update local vars
                self.field_size = int(map_size)
                self.selected_map_id = map_id

                # Unblock button "Place ships"
                self.place_ships_b.config(state=NORMAL)
                self.start_game_b.config(state=NORMAL)
            else:
                # Unblock the buttons
                self.go_to_maps_b.config(state=NORMAL)
                self.create_map_b.config(state=NORMAL)

                # Update notification area
                err_msg = error_code_to_string(resp_code)
                self.add_notification(err_msg)

        # +
        elif command == COMMAND.JOIN_EXISTING_GAME:
            if resp_code == RESP.MAP_DOES_NOT_EXIST:
                self.add_notification("Requested map doesn't exist")
                self.unfreeze_connect_to_map_buttons()

            elif resp_code == RESP.GAME_ALREADY_FINISHED:
                self.add_notification("This game already finished")
                self.unfreeze_connect_to_map_buttons()

            # Game started, but player didn't join the game earlier
            elif resp_code == RESP.GAME_ALREADY_STARTED:
                self.add_notification("Game already started")
                self.unfreeze_connect_to_map_buttons()

            elif resp_code == RESP.MAP_FULL:
                map_name = data
                self.add_notification("Requested map is full")
                self.unfreeze_connect_to_map_buttons()

                # Mark requested map with red color
                # game_started = "1" means the player can't join to this map
                self.mark_map_in_list(map_name, game_started="1")

            else:
                # Run PyGame window to draw the Battlefield
                print "Draw field..."
                self.run_game()

                # Request to get existing shots
                self.client.get_existing_shots()

                if resp_code == RESP.YOU_ARE_IN_SPECTATOR_MODE:
                    # Unblock "spectator mode" button
                    self.spectator_mode_b.config(state=DISABLED)

                    # Launch spectator mode in pygame
                    info = parse_data(data)
                    self.go_to_spectator_mode(info)

                    self.add_notification("You're in spectator mode, you can only observe the game, but not to play")

                else:
                    my_turn, ships_already_placed, game_already_started, owner_id = parse_data(data)

                    # print "JOIN_EXISTING_GAME:", my_turn, ships_already_placed, game_already_started, owner_id

                    if game_already_started == "1":
                        # Unblock "spectator mode" button
                        self.spectator_mode_b.config(state=NORMAL)

                        self.start_game_b.config(state=DISABLED)

                        self.add_notification("Game already started. Please, wait for your turn..")

                        if my_turn == "1":
                            with lock:
                                self.my_turn_to_move = True
                            tkMessageBox.showinfo("Notification", "It's your turn to make move.")

                    else:
                        # Unblock "spectator mode" button
                        self.spectator_mode_b.config(state=NORMAL)

                        self.add_notification("Game hasn't been started yet.")

                        # Ship are not placed yet
                        if ships_already_placed == "0":
                            self.place_ships_b.config(state=NORMAL)

                            self.add_notification("Please, place your ships.")
                        else:
                            self.place_ships_b.config(state=DISABLED)

                    # If I'm admin, then I can start game && kick players
                    if owner_id == self.client.my_player_id:
                        self.kick_player_b.config(state=NORMAL)

                        # If admin still hasn't placed his ships, block button "start"
                        if ships_already_placed == "0":
                            self.start_game_b.config(state=DISABLED)

                        # Unblock "start game" button
                        elif ships_already_placed == "1" and game_already_started == "0":
                            self.start_game_b.config(state=NORMAL)

                        self.add_notification("Your are admin on this map, you can kick players")


                        # elif resp_code in [RESP.OK, RESP.ALREADY_JOINED_TO_MAP, RESP.GAME_ALREADY_STARTED]:
                        #     # # Run PyGame window to draw the Battlefield
                        #     # print "Draw field..."
                        #     # self.run_game()
                        #
                        #     # If player already joined the game
                        #     # Then trigger command to get freshest shots
                        #     if resp_code == RESP.ALREADY_JOINED_TO_MAP:
                        #         self.client.get_existing_shots()
                        #     else:
                        #         self.place_ships_b.config(state=NORMAL)
                        #
                        #     # Unblock "spectator mode" button
                        #     self.spectator_mode_b.config(state=NORMAL)
                        #
                        #     my_turn = data
                        #     if my_turn == "1":
                        #         with lock:
                        #             self.my_turn_to_move = True
                        #
                        # else:
                        #     error = "Command: %s \n" % command_to_str(command)
                        #     error += error_code_to_string(resp_code)
                        #
                        #     self.add_notification(error)
                        #
                        #     # Unblock buttons
                        #     self.unfreeze_connect_to_map_buttons()


        # +
        elif command == COMMAND.PLACE_SHIPS:

            if resp_code == RESP.OK:
                info = parse_data(data)

                self.my_ships_locations = []

                # Parse (x1, x2, y1, y2, and ship size) as tuple
                for i in range(0, len(info), 5):
                    ship = (info[i], info[i + 1], info[i + 2], info[i + 3], info[i + 4])
                    self.my_ships_locations.append(ship)

                # ships_locations = [(x1, x2, y1, y2, ship_size), ...]
                # print self.my_ships_locations

                # Block "Place ships" button
                self.place_ships_b.config(state=DISABLED)

                # Trigger to place ships on the map
                self.place_ships_on_map()

                # Update notification area
                self.add_notification("Ships placed successfully")
            else:
                # Unblock button place ships
                self.place_ships_b.config(state=NORMAL)

                # Update notification area
                error_msg = error_code_to_string(resp_code)
                self.add_notification(error_msg)

        # +
        elif command == COMMAND.MAKE_HIT:

            # In case requested map doesn't exist, then close all windows, and redirect to maps list
            if resp_code == RESP.MAP_DOES_NOT_EXIST:
                self.add_notification("Map doesn't exist")
                self.destroy_previous_root()

                with lock:
                    self.pygame_done = True

                self.choose_map_window()

            elif resp_code == RESP.SHOT_WAS_ALREADY_MADE_HERE:
                self.add_notification("Shot was already made here")

            elif resp_code == RESP.OK:
                # hit - can be successful(1) or not (0)
                target_row, target_column, hit, damaged_player_id = parse_data(data)

                # Update battlefield in pygame
                self.mark_cell(target_row, target_column, hit, damaged_player_id)

                if hit == "1":
                    self.add_notification("Shot was successful")
                    with lock:
                        self.my_turn_to_move = True
                else:
                    self.add_notification("It was missing shot")

                    # TODO: Check whether ship is completely sank

            else:
                # Update notification area
                error_msg = error_code_to_string(resp_code)
                self.add_notification(error_msg)

        # +
        elif command == COMMAND.DISCONNECT_FROM_GAME:
            map_id = data

            # If current map corresponds to map where player played, close it
            if map_id == self.selected_map_id:
                with lock:
                    self.pygame_done = True
                self.destroy_previous_root()

                self.selected_map_id, self.selected_map = None, None

                # Redirect player to another window
                self.choose_map_window()
                self.add_notification("You disconnected successfully")

        # +
        elif command == COMMAND.QUIT_FROM_GAME:
            map_id, map_name = parse_data(data)

            # Destroy Pygame window, and players window
            self.destroy_previous_root()
            with lock:
                self.pygame_done = True

            self.add_notification("You quited successfully from map \"%s\"" % map_name)

        # +
        elif command == COMMAND.START_GAME:
            if resp_code == RESP.OK:
                # Mark that it's creator map turn to make shot
                with lock:
                    self.my_turn_to_move = True

                # Block buttons "place ships"
                self.place_ships_b.config(state=DISABLED)

                self.add_notification("The game started successfully. Now make your shot!")

            else:
                # Unblock "Start game" button
                self.start_game_b.config(state=NORMAL)

                # Show error in status bar
                error_msg = error_code_to_string(resp_code)
                self.add_notification(error_msg)

        elif command == COMMAND.KICK_PLAYER:
            player_id = data

            if resp_code == RESP.OK:
                nickname = self.players_on_map[player_id]["name"]
                # Remove player player list
                # del self.players_on_map[player_id]

                # Update list of players
                self.mark_player_in_list(player_nickname=nickname, kicked=True)

                self.add_notification("Player \"%s\" was successfully kicked" % nickname)

            elif resp_code == RESP.PLAYER_ALREADY_KICKED:
                self.add_notification("Player \"%s\" already kicked" % player_id)

            elif resp_code == RESP.MIN_NUMBER_OF_PLAYERS:
                self.add_notification("You can't kick player, because minimum number of players on map is 2")

        elif command == COMMAND.SPECTATOR_MODE:

            # TODO: Block some buttons
            if data != "":
                info = parse_data(data)
                self.spectator_mode_b.config(state=DISABLED)

                # Launch spectator mode in pygame
                self.go_to_spectator_mode(info)

                self.add_notification("You entered into spectator mode successfully")
            else:
                self.spectator_mode_b.config(state=NORMAL)
                self.add_notification("No ships on the map (so you can't go into spectator mode)")

        # +
        elif command == COMMAND.PLAYERS_ON_MAP:
            # Compressed data in format (map_id, player_id, nickname, disconnected)
            info = parse_data(data)

            # Clean list of current players
            # self.players_l.delete(FIRST, END)

            with lock:
                # Trigger to append current players to the players list
                for i in range(0, len(info), 5):
                    map_id = info[i]

                    # In case of response on old request
                    if map_id != self.selected_map_id:
                        break

                    player_id, player_nickname = info[i + 1], info[i + 2]
                    disconnected = info[i + 3]
                    kicked = info[i + 4]

                    self.players_l.insert(END, player_nickname)
                    self.players_on_map[player_id] = {
                        "name": player_nickname,
                        "disconnected": int(disconnected)
                    }

                    # Mark player in players list
                    if kicked == "1":
                        self.mark_player_in_list(player_nickname, kicked=True)
                    elif disconnected == "1":
                        self.mark_player_in_list(player_nickname, disconnected=True)

                    # If player's ships don't have color, generate a new color
                    if player_id not in self.players_colors.keys():
                        color = self.possible_colors.pop(0)
                        self.players_colors[player_id] = color

                self.add_notification("List of players on this map ws uploaded successfully")

        elif command == COMMAND.MY_SHIPS_ON_MAP:
            # Compressed data in format
            # (map_id, row_start, row_end, column_start, column_end, ship_type, totally_sank)
            info = parse_data(data)

            self.my_ships_locations = []

            with lock:
                # Trigger to color the battlefield with already made shots
                for i in range(0, len(info), 7):
                    map_id = info[i]

                    # In case of response on old request
                    if map_id != self.selected_map_id:
                        break

                    x1, x2 = info[i + 1], info[i + 2]
                    y1, y2 = info[i + 3], info[i + 4]
                    ship_size, totally_sank = info[i + 5], info[i + 6]

                    ##########
                    # Place ships on the map in pygame
                    ship = (x1, x2, y1, y2, ship_size)
                    self.my_ships_locations.append(ship)

            # Trigger to place ships on the map
            self.place_ships_on_map()

            self.add_notification("Your ships locations were uploaded successfully")

        # +
        elif command == COMMAND.EXISTING_SHOTS:
            # Compressed data in format (target_row, target_column, hit_successful, damaged_player_id)
            info = parse_data(data)

            # Trigger to color the battlefield with already made shots
            for i in range(0, len(info), 5):
                map_id = info[i]

                # In case of response on old request
                if map_id != self.selected_map_id:
                    break

                target_row, target_column = info[i + 1], info[i + 2]
                hit_successful, damaged_player_id = info[i + 3], info[i + 4]

                # print damaged_player_id
                if damaged_player_id == "":
                    damaged_player_id = None

                self.mark_cell(target_row, target_column, hit_successful, damaged_player_id)

            self.add_notification("Existing shots uploaded successfully")

        # NOTIFICATIONS FROM SERVER
        # 1) PLAYER_JOINED_TO_GAME
        # 2) ANOTHER_PLAYER_DISCONNECTED
        # 3) YOUR_SHIP_WAS_DAMAGED
        # 4) SOMEONE_MADE_SHOT
        # 5) SOMEONE_TURN_TO_MOVE
        # 6) YOUR_TURN_TO_MOVE (My turn to move)
        # 7) YOU_ARE_KICKED
        # 8) ANOTHER_PLAYER_WAS_KICKED
        # 9) SAVE_PLAYER_ID
        # 10) GAME_STARTED
        # 11) GAME_FINISHED
        # 12) RESTART_GAME

        # +
        elif command == COMMAND.NOTIFICATION.PLAYER_JOINED_TO_GAME:
            player_id, nickname = parse_data(data)

            # If player is already in players list, update his color and his status
            if player_id in self.players_on_map:
                self.players_on_map[player_id]["disconnected"] = "0"

                # Set default color for connected player
                self.mark_player_in_list(nickname)

                self.add_notification("Existing player \"%s\" connected to game" % nickname)
            else:
                self.players_on_map[player_id] = {
                    "name": nickname,
                    "disconnected": "0"
                }

                # Add player nickname to the list of players
                if self.players_l:
                    self.players_l.insert(END, nickname)

                # GUI update status bar about joined player
                self.add_notification("New player %s joined to game" % nickname)

        # +
        elif command == COMMAND.NOTIFICATION.ANOTHER_PLAYER_DISCONNECTED:
            player_id, player_nickname = parse_data(data)

            self.players_on_map[player_id]["disconnected"] = "1"

            # Mark player with gray color (means he is disconnected)
            self.mark_player_in_list(player_nickname, disconnected=True)

        # +
        elif command == COMMAND.NOTIFICATION.YOUR_SHIP_WAS_DAMAGED:
            # Update battlefield in pygame
            map_id, initiator_id, target_row, target_column = parse_data(data)

            if map_id == self.selected_map_id:
                self.mark_cell(target_row, target_column,
                               hit_successful="1", damaged_player_id=self.client.my_player_id)

                msg = "Your ship (coord: %s,%s) was damaged by \"%s\"" \
                      % (target_row, target_column, self.players_on_map[initiator_id]["name"])

                # Update notification area
                self.add_notification(msg)

        # +
        elif command == COMMAND.NOTIFICATION.SOMEONE_MADE_SHOT:
            map_id, initiator_id, initiator_nickname, row, column = parse_data(data)

            # print map_id, "<<<<<<<<<<>>>>>>>", self.selected_map_id
            if map_id == self.selected_map_id:
                # Mark cell on the map in pygame
                # hit - "0"  # because player shouldn't know about it
                self.mark_cell(row, column, hit_successful="0")

                # Mark player with default color
                self.mark_player_in_list(initiator_nickname, turn=False)

                # Update notification area
                msg = command_to_str(command) + "coord(%s,%s)" % (row, column)
                self.add_notification(msg)

        # +
        elif command == COMMAND.NOTIFICATION.YOUR_TURN_TO_MOVE:
            map_id = data

            # Unblock the possibility to make shot
            with lock:
                self.my_turn_to_move = True

            msg = "It's your turn to make move"
            # msg = "It's your turn to make move on map \"%s\"." % self.maps[map_id]["name"]

            # Add notification as pop-up window
            tkMessageBox.showinfo("Notification", msg)
            self.add_notification(msg)

        elif command == COMMAND.NOTIFICATION.SOMEONE_TURN_TO_MOVE:
            player_nickname = data
            self.mark_player_in_list(player_nickname, turn=True)

        # +
        elif command == COMMAND.NOTIFICATION.YOU_ARE_KICKED:
            map_id = data

            if map_id == self.selected_map_id:
                map_name = self.selected_map

                # Reset selected map and its id
                self.selected_map_id, self.selected_map = None, None

                # Destroy players window
                # self.players_root.destroy()

                # Destroy battlefield
                with lock:
                    self.pygame_done = True

                tkMessageBox.showinfo("Kicked", "You was kicked from the map" % map_name)

                self.choose_map_window()

        elif command == COMMAND.NOTIFICATION.ANOTHER_PLAYER_WAS_KICKED:
            kicked_player_id, player_nickname = parse_data(data)

            # Mark player with red color
            self.mark_player_in_list(player_nickname, kicked=True)

            self.add_notification("Admin kicked player %s" % player_nickname)

        # +
        elif command == COMMAND.NOTIFICATION.SAVE_PLAYER_ID:
            # Save player_id
            with lock:
                self.client.my_player_id = data

        # +
        elif command == COMMAND.NOTIFICATION.GAME_STARTED:
            map_id = data

            if map_id == self.selected_map_id:
                map_name = self.selected_map

                self.add_notification("Game on the map \"%s\" started!" % map_name)

        # +
        elif command == COMMAND.NOTIFICATION.GAME_FINISHED:
            map_id, map_name, owner_id = parse_data(data)

            self.add_notification("Game on the map %s finished" % map_name)

            # Current map corresponds to map where player plays
            if map_id == self.selected_map_id:
                # Block buttons kick player and disconnect
                self.kick_player_b.config(state=DISABLED)
                self.disconnect_b.config(state=DISABLED)

                # Unblock button restart the game (if you're owner of this map
                if owner_id == self.client.my_player_id:
                    self.restart_game_b.config(state=NORMAL)

        # +
        elif command in [COMMAND.RESTART_GAME, COMMAND.NOTIFICATION.RESTART_GAME]:
            # Destroy existing window
            with lock:
                self.pygame_done = True

            server_id, map_id, map_name, admin_nickname = parse_data(data)

            # Update local vars
            self.selected_map_id = map_id
            self.selected_server_id = server_id

            self.add_notification("Admin \"%s\" restarted the map \"%s\", you'll be redirected to this map now"
                                  % (admin_nickname, map_name))

            # Trigger join this game
            self.client.join_game()

        elif command == COMMAND.NOTIFICATION.YOU_ARE_NEW_ADMIN:
            map_id, map_name, previous_admin_name, game_started, ships_placed = parse_data(data)

            # Unblock button "Start game"
            if game_started == "0" and ships_placed == "1":
                self.start_game_b.config(state=NORMAL)

            # Unblock button "Kick player"
            self.kick_player_b.config(state=NORMAL)

            self.add_notification("Admin \"%s\" quitted, now you're new admin on the map \"%s\""
                                  % (previous_admin_name, map_name))

        elif command == COMMAND.NOTIFICATION.ANOTHER_PLAYER_QUITTED:
            map_id, map_name, quitted_player_nickname = parse_data(data)

            self.add_notification("Player \"%s\" quitted from the map \"%s\""
                                  % (quitted_player_nickname, map_name))

            # Delete quitted player_name from players list
            if map_id == self.selected_map_id:
                self.remove_player_from_players_list(quitted_player_nickname)
