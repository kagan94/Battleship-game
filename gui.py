import pygame
import tkMessageBox
from Tkinter import *
from ScrolledText import *
from threading import Thread


class GUI(object):
    def __init__(self):
        self.client = None
        self.root = None
        self.frame = None

        self.selected_server = None
        self.selected_server_id = None

        self.maps = {}
        self.selected_map = None
        self.selected_map_id = None

    def nickname_window(self):
        self.root = Tk()
        self.root.title("Enter a nickname")

        self.frame = Frame(self.root)
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack(pady=10, padx=10)

        self.name = Label(self.root, text="Enter a nickname")
        self.name.pack()
        self.nickname = StringVar()
        self.e = Entry(self.root, textvariable=self.nickname)
        self.e.pack()


        self.check_nick_button = Button(self.root, text="Choose", command=self.on_nickname_submit)
        self.check_nick_button.pack()
        self.root.mainloop()

    def choose_server_window(self):
        # Destroy previous window
        if self.root:
            self.root.destroy()

        self.root = Tk()
        self.root.title("Choose a server")

        self.frame = Frame(self.root)
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack(pady=10, padx=10)

        self.server = Label(self.root, text="Choose a server")
        self.server.pack()

        # Servers on-line list
        self.servers_list = Listbox(self.root, height=12)
        self.servers_list.pack()
        self.servers_list.bind('<<ListboxSelect>>', self.on_server_selection)

        # Join server button
        self.join_server_b = Button(self.root, text="Connect", command=self.select_map_window)
        self.join_server_b.pack()

        # if self.select_map_window is None:
        #     self.select_map_window()

        # Show client which servers are on-line (get from Redis)
        self.servers_online = self.client.available_servers()

        for server_name in self.servers_online.values():
            self.servers_list.insert(END, server_name + "\n")

        self.root.mainloop()

    def select_map_window(self):
        # Destroy previous window
        if self.root:
            self.root.destroy()

        self.selected_map = None

        self.root = Tk()
        self.root.title("Choose a game")

        self.frame = Frame(self.root)
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack(pady=10, padx=10)

        self.game_l = Label(self.root, text="Choose a game")
        self.game_l.pack()

        # Available maps
        self.maps_list = Listbox(self.root, height=12)
        self.maps_list.pack()
        self.maps_list.bind('<<ListboxSelect>>', self.on_server_selection)


        # Join server button
        self.join_game_b = Button(self.root, text="Connect to selected map", command=self.on_connect_to_map)
        self.join_game_b.pack()
        self.create_new_game_b = Button(self.root, text="Create new map", command=self.create_new_game_window)
        self.create_new_game_b.pack()

        # Show available servers on this server
        self.client.available_maps()

        # TODO: Add here list of possible games on this

        # self.root.after(500, self.do_stuff)
        self.root.mainloop()

        # while True:
        #     self.root.update_idletasks()
        #     self.root.update()

    # def do_stuff(self, event=None):
    #     if len(self.maps) == 0:
    #         # Do recheck every 500 ms
    #
    #         self.root.after(500, self.do_stuff)

    def update_maps_list(self):
        '''
        Update list of maps inside window choose maps

        :param maps: (dict) map_id: map_name
        '''
        # self.maps is a dict[map_id] = {"name":map_name, "size": [rows, columns]]

        for map_params in self.maps.values():
            print map_params["name"]
            # map_params["name"] + "\n"
            self.maps_list.insert(END, "76767")

    def on_connect_to_map(self):
        if self.selected_map is None:
            self.join_game_b.config(state=DISABLED)
            self.create_new_game_b.config(state=DISABLED)

            # TODO: Request to connect to the map

    def create_new_game_window(self):
        self.root.destroy()
        self.root = Tk()
        self.root.title("Create new game")

        self.gamelistframe = Frame(self.root)
        self.gamelistframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.gamelistframe.columnconfigure(0, weight=1)
        self.gamelistframe.rowconfigure(0, weight=1)
        self.gamelistframe.pack(pady=10, padx=10)

        self.field = Label(self.root, text="Select a size of the field")
        self.field.pack()

        self.size=20

        choices = {
            'S',
            'M',
            'L',
        }

        self.field_size = StringVar(self.root)
        self.option = OptionMenu(self.gamelistframe, self.field_size, *choices)

        # Set default field size to "Small"
        self.field_size.set('S')

        self.option.grid(row=1, column=1)

        def change_size(*args):
            global size
            self.choice = self.field_size.get()

            if self.choice == "S": self.size = 20
            elif self.choice == "M": self.size = 40
            elif self.choice == "L": self.size = 50

        # trace the change of var
        self.field_size.trace('w', change_size)

        self.b = Button(self.root, text="OK", command=self.main)
        self.b.pack()
        self.root.mainloop()

    def main(self):
        # Define some colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)

        # This sets the WIDTH and HEIGHT of each grid location
        WIDTH = 12
        HEIGHT = 12

        # This sets the margin between each cell
        MARGIN = 2

        # Create a 2 dimensional array. A two dimensional
        # array is simply a list of lists.
        self.grid = []

        for self.row in range(self.size):
            # Add an empty array that will hold each cell
            # in this row
            self.grid.append([])
            for self.column in range(self.size):
                self.grid[self.row].append(0)  # Append a cell

        # Set row 1, cell 5 to one.
        # (Remember rows and column numbers start at zero.)
        self.grid[1][5] = 1

        # Initialize pygame
        pygame.init()

        # Set the HEIGHT and WIDTH of the screen
        self.WINDOW_SIZE = [(WIDTH + MARGIN) * self.size + MARGIN,
                            (WIDTH + MARGIN) * self.size + MARGIN]
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)

        # Set title of screen
        pygame.display.set_caption("Battleship game")

        # Loop until the user clicks the close button.
        done = False

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        # -------- Main Program Loop -----------
        while not done:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # User clicks the mouse. Get the position
                    pos = pygame.mouse.get_pos()

                    # Change the x/y screen coordinates to grid coordinates
                    self.column = pos[0] // (WIDTH + MARGIN)
                    self.row = pos[1] // (HEIGHT + MARGIN)

                    # Set that location to one
                    self.grid[self.row][self.column] = 1
                    print("Click ", pos, "Grid coordinates: ", self.row, self.column)

            # Set the screen background
            self.screen.fill(BLACK)

            # Draw the grid
            for self.row in range(self.size):
                for self.column in range(self.size):
                    self.color = WHITE
                    if self.grid[self.row][self.column] == 1:
                        self.color = GREEN

                    pygame.draw.rect(self.screen,
                                     self.color,
                                     [(MARGIN + WIDTH) * self.column + MARGIN,
                                      (MARGIN + HEIGHT) * self.row + MARGIN,
                                      WIDTH,
                                      HEIGHT])

            # Limit to 60 frames per second
            clock.tick(60)

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

        # Be IDLE friendly. If you forget this line, the program will 'hang'
        # on exit.
        pygame.quit()

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
            self.selected_server = selected_server

            # Get selected server_id by selected server name
            self.selected_server_id = self.servers_online.keys()[
                                        self.servers_online.values().index(selected_server)]

            print self.selected_server, self.selected_server_id

            self.client.chosen_server_id = self.selected_server_id



# if __name__ == '__main__':
    # gui = GUI()
    # gui.nickname_window()

