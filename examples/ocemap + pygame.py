# ToggleButton examples.

import pygame, pygame.locals
from ocempgui.widgets import CheckButton

# Initialize the drawing window.
pygame.init()
screen = pygame.display.set_mode((200, 200))
screen.fill((250, 250, 250))
pygame.display.set_caption('ToggleButton')

# Create and display a normal CheckButton.
# button = CheckButton("CheckButton")
# surface = button.draw()
# screen.blit(surface, (5, 5))

# Create a mnemonic ToggleButton, which is active.
button = CheckButton("#Active CheckButton")
button.focus = True
button.active = True
# surface = button.draws()
# screen.blit(surface, (5, 40))

# Show anything.
pygame.display.flip()

# Wait for input.
while not pygame.event.get([pygame.locals.QUIT]):
    pass