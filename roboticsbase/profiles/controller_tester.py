import pygame
import time
import threading
from controller import init_gamepad

def event_tester(joystick):
    exit = False
    
    while exit == False:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                print event
                if event.button == 0:
                    exit = True
        for x in range(joystick.get_numaxes()):
            if (joystick.get_axis(x) != 0):
                print "Axis %d: %d" % (x, joystick.get_axis(x))
        time.sleep(0.25)
        
    pygame.quit()
    
def main():
    pygame.init()
    joystick = init_gamepad()
    print "Starting controller test"
    t = threading.Thread(target=event_tester, args=(joystick))
    t.start()
    
main()
