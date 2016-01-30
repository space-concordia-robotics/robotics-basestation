from roboticsnet.gateway_constants import *
from roboticsnet.roboticsnet_exception import RoboticsnetException
from roboticsnet.rover_client import RoverClient
from multiprocessing import Process, Pipe

class ClientProcess():
    """
    This class describes a client process manager which creates a client on its
    own process, then can pass messages to that client through a pipe. This is to
    establish a single point of contact per client port (avoiding race conditions
    on a shoddy connection) though many client process managers can be established
    on different ports if need be.

    It is the responsibility of the programmer to ensure that no two client processes
    are established on the same host/port.

    TODO: Additional error checking and behaviour, should be updated as new commands are needed

    author: msnidal
    """

    def __init__(self, host, tcp_port, udp_port):
        """
        Initializes a rover client process on host:port
        """

        self.kill_flag = False
        self.state_alive = True
        self.parent_conn, child_conn = Pipe()
        self.process = Process(target=self.client_proc, args=(host, tcp_port, udp_port, child_conn))
        self.process.start()

    def __del__(self):
        """
        Destroys the client process
        """

        kill_client_process()
        self.process.join()

    def send_command(self, command, value = None):
        """
        Send a command to the client process
        """

        if (self.state_alive):
            self.parent_conn.send([command, value])
        else:
            print "Client process dead."

    def set_host(self, host):
        """
        Change the destination host
        """

        if (self.state_alive):
            self.parent_conn.send([ROBOTICSNET_STRCMD_LOOKUP['sethost'], host])
        else:
            print "Client process dead."


    def set_port(self, port, is_tcp):
        """
        Change the destination port
        """

        if (self.state_alive):
            self.parent_conn.send([ROBOTICSNET_STRCMD_LOOKUP['setport'], port, is_tcp])
        else:
            print "Client process dead."


    def kill_client_process(self):
        """
        Kill the process
        """

        if (self.state_alive):
            self.parent_conn.send([ROBOTICSNET_STRCMD_LOOKUP['killclient']])
        else:
            print "Client process dead."

    def client_proc(self, client_host, client_tcp_port, client_udp_port, conn):
        """
        Client process logic loop
        """

        # try init rover client
        try:
            print "Initializing client on {0}:{1}/{2}".format(client_host, client_tcp_port, client_udp_port)
            client = RoverClient(host = client_host, tcp_port = client_tcp_port, udp_port = client_udp_port)
        except Exception as e:
            print "Error initializing rover client!"
            print e.message
            self.kill_flag = True

        # main loop
        while not self.kill_flag:
            try:
                msg = conn.recv()
                print "Sending {0}...".format(msg)
                if (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['graceful']):
                    client.graceful()
                    self.kill_flag = True
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['forward']):
                    client.forward(msg[1])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['reverse']):
                    client.reverse(msg[1])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['forwardLeft']):
                    client.forwardLeft(msg[1])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['forwardRight']):
                    client.forwardRight(msg[1])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['reverseLeft']):
                    client.reverseLeft(msg[1])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['reverseRight']):
                    client.reverseRight(msg[1])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['stop']):
                    client.stop()
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['queryproc']):
                    client.query()
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['startvid']):
                    client.startVideo()
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['stopvid']):
                    client.stopVideo()
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['setport']):
                    client.setPort(msg[1], msg[2])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['sethost']):
                    client.setHost(msg[1])
                elif (msg[0] == ROBOTICSNET_STRCMD_LOOKUP['killclient']):
                    self.kill_flag = True
                else:
                    raise Exception('Message type {0} not matched to a client message. Check clientproc.py').format(msg[0])

                print "{0} sent!".format(msg)

            except Exception as e:
                # put weak connection behaviour here! this means that the station connection is very weak
                print "Exception in station client process! Waiting for next command."
                print e.message

        print "Client process on {0}:{1}/{2} terminated.".format(client_host, client_tcp_port, client_udp_port)
        self.state_alive = False
