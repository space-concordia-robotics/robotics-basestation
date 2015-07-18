import pygame
import time
import threading

from common_constants import *
from roboticsnet.gateway_constants import *
from profiles.logitech_F310 import *

from station_client import send_command

def init_gamepad():    
    if (pygame.joystick.get_count() > 0):
        joystick = pygame.joystick.Joystick(JOYSTICK_ID)
        joystick.init()
        print "Joystick active on slot %d. Using %s profile" % (JOYSTICK_ID, JOYSTICK_NAME)
        return joystick
    else:
        print "Error - no joystick detected."
        return 0

def get_joystick_value(joystick):
    # temp mapping values - waiting on finalized hook values
    x = int(joystick.get_axis(AXIS_RSTICK_X)*128+128)
    y = int((-joystick.get_axis(AXIS_RSTICK_Y))*128+128)
    
    return (x,y)

def joystick_listener(joystick, host, port, events):    
    while events[STOP_CONTROLLER_EVENT].is_set() == False:
        # Button logic
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.joy == JOYSTICK_ID and event.button == BUTTON_A:
                    events[STOP_CONTROLLER_EVENT].set()
                elif event.joy == JOYSTICK_ID and event.button == BUTTON_B:
                    events[VID_STREAM_EVENT].set()
                elif event.joy == JOYSTICK_ID and event.button == BUTTON_X:
                    events[VID_STOP_EVENT].set()
                # elif...
        
        # Joystick logic
        (x,y) = get_joystick_value(joystick)
        
        print "X: %d\nY: %d" % (x,y)
        
        if x < (128-30):
            print "left %d" % x
            send_command(ROBOTICSNET_COMMAND_TURNLEFT, x, host, port)
            
        elif x > (128+30):
            print "right %d" % x
            send_command(ROBOTICSNET_COMMAND_TURNRIGHT, x, host, port)
            
        elif y > (128+10):
            print "forward %d" % y
            send_command(ROBOTICSNET_COMMAND_FORWARD, x, host, port)
    
        elif y < (128-10):
            print "reverse %d" % y
            send_command(ROBOTICSNET_COMMAND_REVERSE, x, host, port)
                
        else:
            print "stop"
            send_command(ROBOTICSNET_COMMAND_STOP, 0, host, port)
        
        time.sleep(0.25)
    
    # send one final stop command
    send_command(ROBOTICSNET_COMMAND_STOP, 0, host, port)
    pygame.quit()
    
def spawn_joystick_thread(host, port, events):
    pygame.init()
    joystick = init_gamepad()
    if (joystick == 0):
        print "Cannot start listener thread without joystick - connect a controller and try again."
        pygame.quit()
    else:
        print "Starting joystick listener thread..."
        t = threading.Thread(target=joystick_listener, args=(joystick, host, port, events))
        t.start()

def main():
    e = [threading.Event() for i in range(NUM_BUTTON_EVENTS)]
    spawn_joystick_thread('localhost', 5000, e)
    
main()

