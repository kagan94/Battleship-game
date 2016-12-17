import pygame
from ocempgui.widgets import *
from ocempgui.widgets.components import TextListItem
from ocempgui.widgets.Constants import *

from threading import Thread


class GUI(object):

    def main(self, size=20):
        re = Renderer()

        # Define some colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)

        self.size=size

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

        # Set row 1, cell 5 to one. (Remember rows and
        # column numbers start at zero.)
        self.grid[1][5] = 1

        # Initialize pygame
        pygame.init()

        # Set the HEIGHT and WIDTH of the screen
        re.create_screen(((WIDTH+MARGIN)*size+MARGIN)*2, (WIDTH+MARGIN)*size+MARGIN)


        self.WINDOW_SIZE = [((WIDTH+MARGIN)*size+MARGIN)*2, (WIDTH+MARGIN)*size+MARGIN]
        # re.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        # self.screen = pygame.display.set_mode(self.WINDOW_SIZE)

        # Set title of screen
        pygame.display.set_caption("Battleship game")

        # Loop until the user clicks the close button.
        done = False

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()





        always = ScrolledList(200, 200)
        always.scrolling = SCROLL_ALWAYS
        always.selectionmode = SELECTION_SINGLE
        always = ScrolledList(200, 200)
        always.scrolling = SCROLL_ALWAYS
        always.selectionmode = SELECTION_SINGLE

        for i in xrange(15):
            item = None
            if i % 2 == 0:
                item = TextListItem("Short item %d" % i)
            else:
                text = "Very, " + 3 * "very, very," + "long item %d" % i
                item = TextListItem(text)
            always.items.append(item)

        # always.topleft = 5, 5
        re.add_widget(always)
        # re.start()

        # self.temp_mainloop_p = Thread(target=re.start)
        # self.temp_mainloop_p.setDaemon(True)
        # self.temp_mainloop_p.start()


        surface2 = always.draw_bg()

        from ocempgui.draw import String
        from ocempgui.widgets import Table


        # re.add_widget(create_label_view())
        # Start the main rendering loop.


        #     # Draw the grid
        #     for self.row in range(self.size):
        #         for self.column in range(self.size):
        #             self.color = WHITE
        #             if self.grid[self.row][self.column] == 1:
        #                 self.color = GREEN
        #             pygame.draw.rect(self.screen,
        #                              self.color,
        #                              [(MARGIN + WIDTH) * self.column + MARGIN,
        #                              (MARGIN + HEIGHT) * self.row + MARGIN,
        #                              WIDTH,
        #                              HEIGHT])


        re.start()

        # -------- Main Program Loop -----------
        # while not done:
        #     for event in pygame.event.get():  # User did something
        #         if event.type == pygame.QUIT:  # If user clicked close
        #             done = True  # Flag that we are done so we exit this loop
        #         elif event.type == pygame.MOUSEBUTTONDOWN:
        #             # User clicks the mouse. Get the position
        #             pos = pygame.mouse.get_pos()
        #             # Change the x/y screen coordinates to grid coordinates
        #             self.column = pos[0] // (WIDTH + MARGIN)
        #             self.row = pos[1] // (HEIGHT + MARGIN)
        #
        #             # Set that location to one
        #             self.grid[self.row][self.column] = 1
        #
        #             print("Click ", pos, "Grid coordinates: ", self.row, self.column)
        #
        #     # Set the screen background
        #     self.screen.fill(BLACK)
        #
        #     # Draw the grid
        #     for self.row in range(self.size):
        #         for self.column in range(self.size):
        #             self.color = WHITE
        #             if self.grid[self.row][self.column] == 1:
        #                 self.color = GREEN
        #             pygame.draw.rect(self.screen,
        #                              self.color,
        #                              [(MARGIN + WIDTH) * self.column + MARGIN,
        #                              (MARGIN + HEIGHT) * self.row + MARGIN,
        #                              WIDTH,
        #                              HEIGHT])
        #
        #     # Limit to 60 frames per second
        #     clock.tick(60)
        #
        #     self.screen.blit(surface2, (((WIDTH+MARGIN)*size+MARGIN),0))
        #     # Go ahead and update the screen with what we've drawn.
        #     pygame.display.flip()
        #
        #
        #     text = String.draw_string_with_bg("This is Times", "Times", 16, 1, (0, 0, 0),
        #                                       (0, 200, 0))
        #     self.screen.blit(text, (5, 60))
        #
        # # Be IDLE friendly. If you forget this line, the program will 'hang'
        # # on exit.
        # pygame.quit()

# if __name__ == '__main__':
#     gui = GUI()
#     gui.main()


import Tkinter as tk


def demo(master):
    listbox = tk.Listbox(master)
    listbox.pack(expand=1, fill="both")

    # inserting some items
    listbox.insert("end", "A list item")

    for item in ["one", "two", "three", "four"]:
        listbox.insert("end", item)

    # this changes the background colour of the 2nd item
    listbox.itemconfig(1, {'bg':'red'})

    # this changes the font color of the 4th item
    listbox.itemconfig(3, {'fg': 'blue'})
    listbox.itemconfig(4, {'bg': 'gray'})

    # another way to pass the colour
    listbox.itemconfig(2, bg=None)

    # print "bg", listbox.itemcget(0, "bg")
    # listbox.itemconfig(2, bg=tk.NORMAL)

    # listbox.itemconfig(2, bg='green')
    # listbox.itemconfig(0, foreground="purple")

    # listbox.itemconfig(0, highlightline="purple")


    els = listbox.get(0, tk.END)

    for i, el in enumerate(els):
        print i, el, type(i)

    listbox.itemconfig(i, bg='green')
    # listbox.itemconfig(i, bg='green')




if __name__ == "__main__":
    root = tk.Tk()
    demo(root)
    root.mainloop()
