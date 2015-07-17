#!/usr/bin/env python3

import pygame
import time
import threading
from controller import initGamepad

def eventTester(joystick):
    exit = False
    
    while exit == False:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                print event
                if event.button == 0:
                    exit = True
        for x in range(joystick.get_numaxes()):
            if (joystick.get_axis(x) != 0):
                print "Axis {0}: {1}".format(x, joystick.get_axis(x))
        time.sleep(0.25)
        
    pygame.quit()
    
def main():
    pygame.init()
    joystick = initGamepad()
    print "Starting controller test"
    t = threading.Thread(target=eventTester(joystick), args=())
    t.start()
    
main()
