#!/usr/bin/env python3

import pygame
import math
import time

pygame.init()

#Loop until the user clicks the currently nonexistent close button.
done = False

# Initialize the joysticks
pygame.joystick.init()


# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
    # Get count of joysticks
    #joystick_count = pygame.joystick.get_count()
    # For each joystick:
    #joystick = pygame.joystick.Joystick(0)
    #joystick.init()
    # Get the name from the OS for the controller/joystick
    #name = joystick.get_name()

    #axes = joystick.get_numaxes()

    print -joystick.get_axis(3),joystick.get_axis(2)
    time.sleep(0.125)

pygame.quit ()

