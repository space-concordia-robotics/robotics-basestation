#!/usr/bin/env python3

import pygame
import time
import threading



def listenjoystick():
    pygame.init()
        
    #Loop until the user clicks the currently nonexistent close button.
    done = False

    # Initialize the joysticks
    pygame.joystick.init()
    
    # FIXME: this is a naive implementation for now
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
    
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
        #for exit button
    
    
        buttons = joystick.get_numbuttons()
        if joystick.get_button(0)>0:
            exit()
        y=(-joystick.get_axis(3))*64
        x=(joystick.get_axis(2)+1)*128
        if x<80:
            print "turn left"
        elif x>170:
            print "turn right"
        elif y > 0:
            print "forward",int(192-y),int(64-y)
    
        
        #print x,y
        time.sleep(0.125)
    
    pygame.quit ()


t = threading.Thread(target=listenjoystick, args=())
t.start()

