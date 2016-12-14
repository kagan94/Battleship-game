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
        self.join_game_b = None
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
        self.notifications = ScrolledText(self.root, width=20, height=20, state=NORMAL)
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
        self.join_game_b = Button(self.select_map_root, text="Connect to selected map",
                                  command=self.run_game, state=DISABLED)
        # command=self.on_connect_to_map, state=DISABLED)
        self.join_game_b.pack()

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

            if choice == "S": self.field_size = 20
            elif choice == "M": self.field_size = 40
            elif choice == "L": self.field_size = 50

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

        self.players_l = ScrolledText(self.players_root, width=12, height=15)
        self.players_l.pack()

        self.place_ships_b = Button(self.players_root, state=NORMAL,
                                    text="Place ships", command=self.on_place_ships)
        self.place_ships_b.pack(padx=10, pady=10)

        # Spectator mode
        self.spectator_mode_b = Button(self.players_root, state=NORMAL,
                                       text="Spectator mode", command=self.client.spectator_mode)
        self.spectator_mode_b.pack(padx=10, pady=10)

        # Kick player
        self.kick_player_b = Button(self.players_root, state=DISABLED,
                                    text="Kick selected player", command=self.on_kick_player)
        self.kick_player_b.pack(padx=5, pady=5)

        # Disconnect from the game
        self.disconnect_b = Button(self.players_root, text="Disconnect", command=self.on_disconnect)
        self.disconnect_b.pack()

        # Quit
        self.quit_b = Button(self.players_root, text="Quit from the game", command=self.on_quit)
        self.quit_b.pack()

    def run_game(self):
        # Destroy previous window
        self.destroy_previous_root()

        self.players_on_map_window()

        # Request to get all players on the map and player's ships
        self.client.my_ships_on_map()
        self.client.players_on_map()

        # print "RUN GAME"

        # Create new thread to draw field
        field_t = Thread(target=self.draw_field)
        field_t.setDaemon(True)
        field_t.start()

    def draw_field(self):
        '''' Here we draw our field and parse changes '''

        # If the map_size is unknown, then exit
        if self.field_size is None:
            return

        field_name = self.selected_map
        self.my_ships_locations = []
        self.players_on_map = {}  # key - player_id, value - dict("name":nickname, "disconnected":val)

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
        done = False

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        def draw_dash(i, j):
            # print i, j
            # x1, x2 = 20, 20 + MARGIN + WIDTH
            # y1, y2 = 120, 120
            # i, j = 19, 19

            x1 = (MARGIN + WIDTH) * j
            x2 = (MARGIN + WIDTH) * j + MARGIN + WIDTH
            y1 = y2 = (MARGIN + HEIGHT) * i - ((MARGIN + HEIGHT) / 2)

            # if y2 > self.maxx:
            #     self.maxx = y2
            #     print x1, x2, "_____"

            # x1, x2, y2 = 0, 14, 275
            y1 = y2

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
        while not done:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

                elif event.type == pygame.MOUSEBUTTONDOWN:
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
                    if cell not in self.players_colors.keys() and cell not in self.shots_colors.keys():
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

                    # My ships
                    if key == -1:
                        color = BLACK

                    # In this case 'key" = player_id
                    # if key in self.players_colors.keys():
                    #     color = self.players_colors[key]
                    #     # self.color = GREEN
                    #
                    # if key in self.shots_colors.keys():
                    #     color = self.shots_colors[key]
                    #
                    #     # For cases:
                    #     # - My ship was damaged
                    #     # - My hit was successful
                    #     if key in [-10, -11]:
                    #         draw_cross(row, column)
                    #
                    #     # Someone made a shot, but missed
                    #     elif key == -12:
                    draw_dash(row, column)

                        # else:
                        #     draw_dash
                    pygame.draw.rect(self.screen,
                                     color,
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])

                    # pygame.draw.line(self.screen, self.color,
                    #                  (0, 100), (50, 100)
                    #                  )


                    # pygame.draw.line(self.screen, BLACK, (120, 100), (195, 195), 3)
                    # pygame.draw.line(self.screen, BLACK, (195, 100), (120, 195), 3)
            # except IndexError:
            #     pass



            # x3 = (MARGIN + WIDTH) * self.row


            # pygame.draw.line(self.screen, BLACK, (x3, x1), (x2, x3), 4)

            # print self.pygame_tasks._qsize()
            # try:
            #     task = self.pygame_tasks.get(False)
            #
            # # Handle empty queue here
            # except Queue.Empty:
            #     pass
            # else:
            #     # Handle task here and call q.task_done()
            #     # GAME_COMMAND.PLACE_SHIPS
            #     # self.process_pygame_task(task)
            #     print task
            #     with lock:
            #         print self.my_ships_locations

                # self.pygame_tasks.task_done()

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
                            print i, j
                            self.grid[i][j] = -12
                            # self.grid[i][j] = self.client.my_player_id
                    # print x1, x2, y1, y2

            except AttributeError:
                pass

    def go_to_spectator_mode(self, info):
        ''' Spectator mode allows to see all ships of all players '''

        # Parse (player_id, x1, x2, y1, y2, and ship size) as tuple
        with lock:
            for k in range(0, len(info), 6):
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

    def mark_cell(self, target_row, target_column, hit_successful, my_ship_was_damaged=False, damaged_player_id=None):
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
            # Depending on whether the hit was successful or not, mark cell differently
            if my_ship_was_damaged:
                self.grid[i][j] = -10

                if damaged_player_id:
                    self.grid[i][j] = self.players_colors[damaged_player_id]

            # My hit was successful, update the battlefield
            elif hit_successful:
                self.grid[i][j] = -11

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

            print self.selected_server, self.selected_server_id

    def on_game_selection(self, event):
        self.join_game_b.config(state=NORMAL)

        widget = self.maps_list
        try:
            index = int(widget.curselection()[0])
            selected_map = widget.get(index).strip()
        except:
            selected_map = None

        # Only 1 click to connect to particular server is allowed
        if selected_map is not None \
                and (self.selected_map != selected_map) \
                and self.join_game_b.cget("state") == NORMAL:

            # Save selected map name
            self.selected_map = selected_map

            # Get selected map_id by selected map name
            for map_id, map_params in self.maps.items():
                if map_params["name"] == self.selected_map:
                    self.selected_map_id = map_id
                    # print map_params["size"]
                    self.field_size = int(map_params["size"])  # list [rows, columns]
                    break

            # Share access to selected map_id for Client (as attribute)
            self.client.selected_map_id = self.selected_map_id

            print self.selected_map, self.selected_map_id

    def on_connect_to_server(self):
        ''' When player click button "Connect to selected map" '''
        if self.selected_server:
            # self.join_server_b.config(state=DISABLED)
            # TODO: Request to connect to the map
            self.choose_map_window()

    def on_connect_to_map(self):
        ''' When player click button "Connect to selected map" '''

        if self.selected_map:
            self.join_game_b.config(state=DISABLED)
            self.create_new_game_b.config(state=DISABLED)

            print "Waiting for response from server"

            self.client.join_game()
            # TODO: Request to connect to the map

    def on_create_map(self):
        # Disable the button create new map with parameters
        # until we will receive response from server
        self.create_map_b.config(state=DISABLED)
        self.go_to_maps_b.config(state=DISABLED)

        # Send request to create new map
        if self.new_map_name.get():
            # Save map name
            self.selected_map = self.new_map_name.get()

            # Request to create new game on server
            self.client.create_new_game(game_name=self.new_map_name.get(), field_size=self.field_size)

    def on_place_ships(self):
        ''' Player wants to place his ships '''
        self.place_ships_b.config(state=DISABLED)

        # Request to place ships
        self.client.place_ships()

    def on_kick_player(self):
        pass
        # TODO: Get selected player name and send request to kick it

    def on_disconnect(self):
        ''' Player wants to disconnect from the game. Should redirect to maps '''
        pass

    def on_quit(self):
        ''' Player wants to quit from the game. Should redirect to maps '''
        pass

    #############################################
    # Other methods
    #############################################
    def destoy_root(self):
        # Destroy previous window
        if self.root:
            self.root.destroy()
            self.root = None

        self.client.resp = None

    def unfreeze_join_game_buttons(self):
        # print self.join_game_b, type(self.join_game_b)

        # Unblock buttons to create or join to the server
        if self.join_game_b and self.create_new_game_b:
            self.join_game_b.config(state=NORMAL)
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

        print self.maps_list

        if self.maps_list:
            try:
                for map_params in self.maps.values():
                    self.maps_list.insert(END, map_params["name"] + "\n")
            except TclError as e:
                print "Error in update maps list"
                return


    # def run_main_loop(self):
    #     ''' This method runs in new Thread and exit when the window closed '''
    #     while True:
    #         if self.root is None:
    #             break
    #
    #         # if self.client.resp is None:
    #         #     self.root.after(10, self.check_resp)  # timeout 10 ms
    #         # else:
    #         #     self.destoy_root()
    #         #     self.client.resp = None
    #         print self.client.resp
    #         # In case some errors show error
    #         # if self.popup_msg:
    #         #     tkMessageBox.showinfo("Notification", self.popup_msg)
    #         #     self.popup_msg = None
    #         # self.root.mainloop()
    #
    #         # Equivalent to self.root.mainloop()
    #         try:
    #             self.root.update_idletasks()
    #             self.root.update()
    #         except TclError:
    #             self.root = None
    #             break
    #
    #         print "window alive"
    #         # Timeout 100 ms between window update
    #         time.sleep(0.1)

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

    ####################
    # Important function to process responses from servers
    ####################
    def process_task(self, task):
        ''' Handler to receive response on request reg_me '''
        command, resp_code, server_id, data = parse_response(task)

        # print command, resp_code, server_id, data

        print ">> Received resp(%s) on command: %s, server(%s)" \
              % (error_code_to_string(resp_code), command_to_str(command), server_id)

        print task

        # +
        if command == COMMAND.LIST_OF_MAPS:
            maps_data = parse_data(data)
            self.maps = {}

            if len(maps_data) == 1 and maps_data[0] == "":
                self.add_notification("No available maps online")

            else:
                # with lock:
                # Decompress maps (map_id, map_name, field size) to dict[map_id] = [params]
                for i in range(0, len(maps_data), 3):
                    map_id = maps_data[i]
                    map_name, field_size = maps_data[i + 1], maps_data[i + 2]

                    self.maps[map_id] = {
                        "name": map_name,
                        "size": field_size
                    }

                self.update_maps_list()
                self.add_notification("List with maps updated successfully")

        # +
        elif command == COMMAND.CREATE_NEW_GAME:
            map_id = data

            if resp_code == RESP.OK:
                # Start the game and open new field
                self.run_game()

            else:
                # Unblock the buttons
                self.go_to_maps_b.config(state=NORMAL)
                self.create_map_b.config(state=NORMAL)

                # Update notification area
                err_msg = error_code_to_string(resp_code)
                self.add_notification(err_msg)

        # +
        elif command == COMMAND.JOIN_EXISTING_GAME:
            if resp_code in [RESP.OK, RESP.ALREADY_JOINED_TO_MAP]:
                print self.field_size
                print self.selected_map_id

                # with lock:
                #     self.resp = True

                self.run_game()

                print "Command draw field"

                # If player already joined the game
                # Then trigger command to get freshest shots
                if resp_code == RESP.ALREADY_JOINED_TO_MAP:
                    self.client.get_existing_shots()

            else:
                error = "Command: %s \n" % command_to_str(command)
                error += error_code_to_string(resp_code)

                self.add_notification(error)

                # Unblock buttons
                self.unfreeze_join_game_buttons()

                # with lock:
                # Show window with error msg + unblock buttons
                # self.show_popup(error)

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

                # with lock:
                #     self.pygame_tasks.put(GAME_COMMAND.PLACE_SHIPS)

                # Trigger to place ships on the map
                self.place_ships_on_map()

                # Update notification area
                self.add_notification("Ships placed successfully")
            else:
                # Unblock button place ships
                self.place_ships_b.config(state=DISABLED)

                # Update notification area
                error_msg = error_code_to_string(resp_code)
                self.add_notification(error_msg)

        # +
        elif command == COMMAND.MAKE_HIT:

            if resp_code == RESP.OK:
                target_row, target_column, hit_successful, damaged_player_id = parse_data(data)


                # Update battlefield in pygame
                self.mark_cell(target_row, target_column, hit_successful, damaged_player_id)

                if hit_successful == "1":
                    self.add_notification("Shot was successful")
                else:
                    self.add_notification("It was missing shot")

                # TODO: Check whether ship is completely sank

            else:
                # Update notification area
                error_msg = error_code_to_string(resp_code)
                self.add_notification(error_msg)

        elif command == COMMAND.DISCONNECT_FROM_GAME:
            pass

        elif command == COMMAND.QUIT_FROM_GAME:
            pass

        elif command == COMMAND.START_GAME:
            pass

        elif command == COMMAND.RESTART_GAME:
            pass

        elif command == COMMAND.KICK_PLAYER:
            pass

        elif command == COMMAND.SPECTATOR_MODE:
            info = parse_data(data)

            # TODO: Block some buttons

            # Launch spectator mode in pygame
            self.go_to_spectator_mode(info)

        # +
        elif command == COMMAND.PLAYERS_ON_MAP:
            # Compressed data in format (map_id, player_id, nickname, disconnected)
            info = parse_data(data)

            # Clean list of current players
            # self.players_l.delete(FIRST, END)

            with lock:
                # Trigger to append current players to the players list
                for i in range(0, len(info), 4):
                    map_id = info[i]

                    # In case of response on old request
                    if map_id != self.selected_map_id:
                        break

                    player_id, player_nickname = info[i + 1], info[i + 2]
                    disconnected = info[i + 3]

                    self.players_l.insert(END, player_nickname)

                    self.players_on_map[player_id] = {
                        "name": player_nickname,
                        "disconnected": int(disconnected)
                    }

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

                self.mark_cell(target_row, target_column, hit_successful, damaged_player_id)

            self.add_notification("Existing shots uploaded successfully")

        # NOTIFICATIONS FROM SERVER
        # 1) If I'm owner of the map and another player joined
        # 2) Another player damaged my ship
        # 3) My ship sank
        # 4) My turn to move
        # 5) You're kicked
        # 6) Another player damaged another player's ship

        # +
        elif command == COMMAND.NOTIFICATION.PLAYER_JOINED_TO_GAME:
            joined_player = data  # nickname
            # (!) Don't need to check resp_code

            # TODO: GUI update status bar about joined player

        elif command == COMMAND.NOTIFICATION.YOUR_SHIP_WAS_DAMAGED:
            # Update battlefield in pygame
            map_id, initiator_id, target_row, target_column = parse_data(data)

            if map_id == self.selected_map_id:
                self.mark_cell(target_row, target_column, None, my_ship_was_damaged=True, damaged_player_id=None)

                # Update notification area
                msg = command_to_str(command) + "coord(%s,%s)" % (target_row, target_column)
                self.add_notification(msg)

        elif command == COMMAND.NOTIFICATION.SOMEONE_MADE_SHOT:
            map_id, initiator_id, row, column = parse_data(data)

            print map_id, "<<<<<<<<<<>>>>>>>", self.selected_map_id
            if map_id == self.selected_map_id:
                hit_successful = None  # because player shouldn't know about it

                # Mark cell on the map in pygame
                self.mark_cell(row, column, hit_successful)

                # Update notification area
                msg = command_to_str(command) + "coord(%s,%s)" % (row, column)
                self.add_notification(msg)

        elif command == COMMAND.NOTIFICATION.YOUR_TURN_TO_MOVE:
            pass

        elif command == COMMAND.NOTIFICATION.YOU_ARE_KICKED:
            pass

        elif command == COMMAND.NOTIFICATION.SAVE_PLAYER_ID:
            with lock:
                self.client.my_player_id = data

        # ????? Do we really need it????????????????????????????????????
        elif command == COMMAND.NOTIFICATION.SOMEONES_SHIP_SANK:
            pass
