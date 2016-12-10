import pygame
from Tkinter import *


def main():
    root = Tk()
    root.title("Size Selector")

    mainframe = Frame(root)
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    mainframe.pack(pady=10, padx=10)

    var = StringVar(root)
    global size
    size = 20

    # Use dictionary to map names to ages.
    choices = {
        'S',
        'M',
        'L',
    }

    option = OptionMenu(mainframe, var, *choices)
    var.set('S')

    option.grid(row=1, column=1)

    # change_age is called on var change.
    def change_size(*args):
        global size
        choice = var.get()

        if choice == "S":
            size = 20
        elif choice == "M":
            size = 40
        elif choice == "L":
            size = 50

    # trace the change of var
    var.trace('w', change_size)

    b = Button(root, text="OK", command= lambda: main2(size))
    b.pack()

    root.mainloop()

def main2(size=20):

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
    grid = []
    for row in range(size):
        # Add an empty array that will hold each cell
        # in this row
        grid.append([])
        for column in range(size):
            grid[row].append(0)  # Append a cell

    # Set row 1, cell 5 to one. (Remember rows and
    # column numbers start at zero.)
    grid[1][5] = 1

    # Initialize pygame
    pygame.init()

    # Set the HEIGHT and WIDTH of the screen
    WINDOW_SIZE = [(WIDTH+MARGIN)*size+MARGIN, (WIDTH+MARGIN)*size+MARGIN]
    screen = pygame.display.set_mode(WINDOW_SIZE)

    # Set title of screen
    pygame.display.set_caption("Array Backed Grid")

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
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)

                # Set that location to one
                grid[row][column] = 1
                print("Click ", pos, "Grid coordinates: ", row, column)

        # Set the screen background
        screen.fill(BLACK)

        # Draw the grid
        for row in range(size):
            for column in range(size):
                color = WHITE
                if grid[row][column] == 1:
                    color = GREEN

                pygame.draw.rect(screen,
                                 color,
                                 [(MARGIN + WIDTH) * column + MARGIN,
                                  (MARGIN + HEIGHT) * row + MARGIN,
                                  WIDTH,
                                  HEIGHT])

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()


if __name__ == '__main__':
    main()
