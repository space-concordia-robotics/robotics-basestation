#!/usr/bin/env python3

import pygame
import os
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
        y=(-joystick.get_axis(3))*63
        x=(joystick.get_axis(2)+1)*128
        if x<80:
            print "turn left"
            leftMotorValue = 96
            rightMotorValue = 224
            sendCommand("forward",leftMotorValue)
            sendCommand("reverse",rightMotorValue)
            
        elif x>170:
            print "turn right"
            leftMotorValue = 32
            rightMotorValue = 160
            sendCommand("reverse",leftMotorValue)
            sendCommand("forward",rightMotorValue) 
            
        elif y > 0:
            y1 = int(193-y)
            y2 = int(65-y)
            print "forward",y1,y2
            sendCommand("forward",y1)
            sendCommand("forward",y2)

        elif y < 0:
            y1 = int(193 + y)
            y2 = int(65 + y)
            print "reverse",y1,y2
            sendCommand("reverse",y1)
            sendCommand("reverse",y2)
            
        else:
            print "stop"
            genericCommand("stop")
        
        #print x,y
        time.sleep(0.125)
    
    pygame.quit ()

# Sends 
def sendCommand(direction, speed):
    os.system("~/Dev/git/robotics-networking/roboticsnet/bin/roboticsnet-client --" + direction + " " + str(speed))
    
def genericCommand(arg):
    os.system("~/Dev/git/robotics-networking/roboticsnet/bin/roboticsnet-client --" + arg)

t = threading.Thread(target=listenjoystick, args=())
t.start()

