#!/usr/bin/env python3

import pygame
import time
import threading
from roboticsnet.client import rover_client

JOYSTICK_ID = 0

def init_gamepad():    
    if (pygame.joystick.get_count() > 0):
        joystick = pygame.joystick.Joystick(JOYSTICK_ID)
        joystick.init()
        print "Joystick active on slot %d" % JOYSTICK_ID
        return joystick
    else:
        print "Error - no joystick detected."
        return 0

def get_joystick_value(joystick):
    # temp mapping values - waiting on finalized hook values
    x = joystick.get_axis(3)*128
    y = (-joystick.get_axis(4))*128
    
    return (x,y)

def joystick_listener(joystick):
    exit = False
    client = rover_client.RoverClient() #host, port temporarily set to default values as per roboticsnet constants. Pass these in from the base station interface?
    print "New client established using host %s and port %d" % (client.getHost(), client.getPort())
     
    while exit == False:
        # Button logic
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.joy == JOYSTICK_ID and event.button == 0:
                    exit = True
                #elif...
        
        # Joystick logic
        (x,y) = get_joystick_value(joystick)
        
        print "X: %d\nY: %d" % (x,y)
        
        if x < -30:
            print "left %d" % x
            #leftMotorValue = 96
            #rightMotorValue = 224
            #client.turnLeft(x)
            
        elif x > 30:
            print "right %d" % x
            #leftMotorValue = 32
            #rightMotorValue = 160
            #client.turnRight(x)
            
        elif y > 10:
            #y1 = int(193-y)
            #y2 = int(65-y)
            print "forward %d" % y
            #client.forward(y)
    
        elif y < -10:
            #y1 = int(193 + y)
            #y2 = int(65 + y)
            print "reverse %d" % y
            #client.forward(y)
                
        else:
            print "stop"
            #client.stop(0)
        
        time.sleep(0.125)
        
    pygame.quit()
    
def spawn_joystick_thread():
    pygame.init()
    joystick = init_gamepad()
    if (joystick == 0):
        print "Cannot start listener thread without joystick - connect a controller and try again."
        pygame.quit()
    else:
        print "Starting joystick listener thread..."
        t = threading.Thread(target=joystick_listener(joystick), args=())
        t.start()

def main():
    spawn_joystick_thread()
    
main()

