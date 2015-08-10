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
        if (command == ROBOTICSNET_COMMAND_GRACEFUL):
            client.graceful()
        elif (command == ROBOTICSNET_COMMAND_FORWARD):
            client.forward(value)
        elif (command == ROBOTICSNET_COMMAND_REVERSE):
            client.reverse(value)
        elif (command == ROBOTICSNET_COMMAND_FORWARDLEFT):
            client.forwardLeft(value)
        elif (command == ROBOTICSNET_COMMAND_FORWARDRIGHT):
            client.forwardRight(value)
        elif (command == ROBOTICSNET_COMMAND_REVERSELEFT):
            client.reverseLeft(value)
        elif (command == ROBOTICSNET_COMMAND_REVERSERIGHT):
            client.reverseRight(value)
        elif (command == ROBOTICSNET_COMMAND_STOP):
            client.stop()
        elif (command == ROBOTICSNET_COMMAND_QUERYPROC):
            client.query()
        elif (command == ROBOTICSNET_COMMAND_START_VID):
            client.startVideo()
        elif (command == ROBOTICSNET_COMMAND_STOP_VID):
            client.stopVideo()
            
        print "Sent %d:%d." % (command, value)

    except RoboticsnetException as e:
        print "Command failed!"
        print e.message

    except Exception as e:
        print "Critical station client failure!"
        print e.message
        
    finally:
        lock.release()
