import pygame
import time
import multiprocessing

from input_exception import InputException

from pygame.locals import *
from common_constants import *
from roboticsnet.gateway_constants import *
from clientproc import ClientProcess

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

def joystick_listener(client_process, events, joystick):
    """
    Main movement control thread - interprets commands from joystick and sends them to rover.
    """

    last = (0, 0)
    while events[ROBOTICSBASE_STOP_LISTENER].is_set() == False:
        # Sleep before starting next cycle
        time.sleep(CONTROLLER_SLEEP_INTERVAL)

        # Button logic
        for event in pygame.event.get():
            if event.type == JOYBUTTONDOWN:
                if event.button == BUTTON_A:
                    events[ROBOTICSBASE_STOP_LISTENER].set()
                elif event.button == BUTTON_B:
                    if events[ROBOTICSBASE_STREAM_VIDEO].is_set():
                        client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['startvid'])
                        events[ROBOTICSBASE_STREAM_VIDEO].clear()
                    else:
                        client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['stopvid'])
                        events[ROBOTICSBASE_STREAM_VIDEO].set()
                # elif...

        # Joystick logic
        (x,y) = get_joystick_value(joystick)
        print "X: %d\nY: %d" % (x,y)

        if (x,y) == last:
            continue

        if x < (-20) and y >= 0:
            print "forward left %d" % x
            client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['forwardLeft'], -x/2)

        elif x > (20) and y >= 0:
            print "forward right %d" % x
            client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['forwardRight'], x/2)


        elif x < (-20) and y < 0:
            print "reversing left %x" % x
            client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['reverseLeft'], -x/2)


        elif x > 20 and y < 0:
            print "reversing right %d" % x
            client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['reverseRight'], x/2)


        elif y > (10):
            print "forward %d" % y
            client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['forward'], y)

        elif y < (-10):
            print "reverse %d" % y
            client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['reverse'], -y)

        else:
            print "stop"
            client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['stop'])
        # Save joystick value
        last = (x,y)

    # send one final stop command. Reset controller stop event
    client_process.send_command(ROBOTICSNET_STRCMD_LOOKUP['stop'])

    pygame.quit()
    print "Joystick thread killed."


def spawn_joystick_process(client_process, events):
    """
    Spawns a joystick input process, which gets input from controller and sends it to the rover.
    events is an array of process events that keep track of basestation events (Such as the stream video command and whether the controller is active)
    lock is a process lock which prevents clients from sending messages concurrently
    """

    pygame.init()
    events[ROBOTICSBASE_STOP_LISTENER].clear()

    try:
        joystick = get_joystick()
        joystick.init()

        joystick_process = multiprocessing.Process(target=joystick_listener, args=(client_process, events, joystick))
        joystick_process.start()

    except InputException as e:
        print "Input error!"
        print e.message
        raise

def main():
    """
    Test method that creates a standalone controller event thread
    """
    host = raw_input("Enter host: ")
    port = int(raw_input("Enter port: "))
    events = [multiprocessing.Event() for i in range(ROBOTICSBASE_NUM_EVENTS)]
    lock = multiprocessing.Lock()
    client_process = ClientProcess(host, port, port+1)

    try:
        spawn_joystick_process(client_process, events)
    except Exception as e:
        client_process.kill_client_process()

if __name__ == "__main__":\
    main()
