from roboticsnet.client.rover_client import RoverClient
from roboticsnet.gateway_constants import *
from roboticsnet.roboticsnet_exception import RoboticsnetException

def send_command(command, host='localhost', port=ROBOTICSNET_PORT, value=0):
    client = RoverClient(host, port)
    print "Using %s:%d:" % (client.getHost(), client.getPort())
    
    try:
        if (command == ROBOTICSNET_COMMAND_GRACEFUL):
            client.graceful()
        elif (command == ROBOTICSNET_COMMAND_FORWARD):
            client.forward(value)
        elif (command == ROBOTICSNET_COMMAND_REVERSE):
            client.reverse(value)
        elif (command == ROBOTICSNET_COMMAND_TURNLEFT):
            client.turnLeft(value)
        elif (command == ROBOTICSNET_COMMAND_TURNRIGHT):
            client.turnRight(value)
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
        print "Station client failed!"
        print e.message

    except Exception as e:
        print "Critical station client failure!"
        print e.message
