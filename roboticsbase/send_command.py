from roboticsnet.gateway_constants import *
from roboticsnet.roboticsnet_exception import RoboticsnetException

def send_locked_command(client, lock, command, value=0):
    """
    Process-safe function to send a command via a passed client.
    By sharing a lock between all processes, we ensure that only one command may be sent at a time (see python multiprocessing documentation)
    """
    
    lock.acquire()
    print "Sending %d to %s:%d:" % (command, client.getHost(), client.getPort())
    
    try:
        """0x20-0x23 are the camera commands"""
        if (command == ROBOTICSNET_SYSTEM_GRACEFUL or command == ROBOTICSNET_SENSOR_INFO or command in range (0x20,0x24)):
            client.sendCommand(command)
            """These are the ROBOTICSNET_DRIVE_... commands"""
        elif (command in range(0x07):
            client.timedCommand(command, value)
        elif (command == ROBOTICSNET_SYSTEM_QUERYPROC):
            client.query()
            
        print "Sent %d:%d." % (command, value)

    except RoboticsnetException as e:
        print "Command failed!"
        print e.message

    except Exception as e:
        print "Critical station client failure!"
        print e.message
        
    finally:
        lock.release()
