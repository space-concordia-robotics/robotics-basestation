import pygame
import time
import multiprocessing

from input_exception import InputException
from send_command import send_locked_command
from roboticsnet.client.rover_client import RoverClient

from pygame.locals import *
from common_constants import *
from roboticsnet.gateway_constants import *

from profiles.logitech_F310 import *

def get_joystick():
    """
    Gets a joystick object from available joysticks.
    Raises an InputException if none are available.
    """
    if (pygame.joystick.get_count() == 0):
        raise InputException("No joystick detected")
    elif (pygame.joystick.get_count() == 1):
        return pygame.joystick.Joystick(0)
    else:
        joystick_id = int(raw_input("Select a joystick from " + range(pygame.joystick.get_count()) + " : "))
        return pygame.joystick.Joystick(joystic_id)

def get_joystick_value(joystick):
    """
    Returns a tuple with X and Y stick values from a gamepad, on a scale from -63 to 63.
    At the moment this only includes the right pad, but it can be extended with other joystick axes as needed.
    """
    x = int(joystick.get_axis(AXIS_RSTICK_X)*63)
    y = int((-joystick.get_axis(AXIS_RSTICK_Y))*63)
    
    return (x,y)

def input_listener(host, port, events, lock, joystick):
    """
    Main movement control thread - interprets commands from joystick and sends them to rover.
    """
    client = RoverClient(host, port)
    print "Controller client established with %s:%d:" % (client.getHost(), client.getPort())
    
    while events[ROBOTICSBASE_STOP_LISTENER].is_set() == False:
        # Button logic
        for event in pygame.event.get():
            if event.type == JOYBUTTONDOWN:
                if event.button == BUTTON_A:
                    events[ROBOTICSBASE_STOP_LISTENER].set()
                elif event.button == BUTTON_B:
                    if events[ROBOTICSBASE_STREAM_VIDEO].is_set():
                        send_locked_command(client, lock, ROBOTICSNET_COMMAND_START_VID)
                        events[ROBOTICSBASE_STREAM_VIDEO].clear()
                    else:
                        send_locked_command(client, lock, ROBOTICSNET_COMMAND_STOP_VID)
                        events[ROBOTICSBASE_STREAM_VIDEO].set()
                # elif...

        # Joystick logic
        (x,y) = get_joystick_value(joystick)
        
        print "X: %d\nY: %d" % (x,y)

        if x < (-20) and y >= 0:
            print "forward left %d" % x
            send_command(ROBOTICSNET_COMMAND_FORWARDLEFT, host, port, -x/2)

        elif x > (20) and y >= 0:
            print "forward right %d" % x
            send_command(ROBOTICSNET_COMMAND_FORWARDRIGHT, host, port, x/2)

        elif x < (-20) and y < 0:
            print "reversing left %x" % x
            send_command(ROBOTICSNET_COMMAND_REVERSELEFT, host, port, x/2)

        elif x > 20 and y < 0:
            print "reversing right %d" % x
            send_command(ROBOTICSNET_COMMAND_REVERSERIGHT, host, port, x/2)

        elif y > (10):
            print "forward %d" % y
            send_locked_command(client, lock, ROBOTICSNET_COMMAND_FORWARD, y)
    
        elif y < (-10):
            print "reverse %d" % y
            send_locked_command(client, lock, ROBOTICSNET_COMMAND_REVERSE, -y)
                
        else:
            print "stop"
            send_locked_command(client, lock, ROBOTICSNET_COMMAND_STOP)
        
        time.sleep(CONTROLLER_SLEEP_INTERVAL)
    
    # send one final stop command. Reset controller stop event
    send_locked_command(client, lock, ROBOTICSNET_COMMAND_STOP)
    events[ROBOTICSBASE_STOP_LISTENER].clear()

def spawn_input_process(host, port, events, lock):
    """
    Spawns an input process, which gets input from keyboard or controller and sends it to the rover.
    events is an array of process events that keep track of basestation events (Such as the stream video command and whether the controller is active)
    lock is a process lock which prevents clients from sending messages concurrently
    """
    
    pygame.init()
    
    try:
        joystick = get_joystick()
        joystick.init()
        
        input_process = multiprocessing.Process(target=input_listener, args=(host, port, events, lock, joystick))
        input_process.start()
        
        # Wait for process to finish, then deinit pygame
        input_process.join()
        
    except InputException as e:
        print "Input error!"
        print e.message
        
    pygame.quit()
    print "Movement process aborted."

def main():
    """
    Test method that creates a standalone controller event thread
    """
    host = raw_input("Enter host: ")
    port = int(raw_input("Enter port: "))
    events = [multiprocessing.Event() for i in range(ROBOTICSBASE_NUM_EVENTS)]
    lock = multiprocessing.Lock()
    spawn_input_process(host, port, events, lock)
    
main()

