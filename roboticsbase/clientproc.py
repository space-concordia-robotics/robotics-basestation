from roboticsnet.gateway_constants import *
from roboticsnet.roboticsnet_exception import RoboticsnetException
from roboticsnet.rover_client import RoverClient
from roboticslogger.logger import Logger
from multiprocessing import Process, Pipe
import socket

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

    def __init__(self, host, tcp_port, udp_port, logger_conn):
        """
        Initializes a rover client process on host:port
        """

        self.kill_flag = False
        self.state_alive = True
        self.logger_conn = logger_conn
        self.parent_conn, child_conn = Pipe()
        self.process = Process(target=self.client_proc, args=(host, tcp_port, udp_port, child_conn))
        self.process.start()

    def __del__(self):
        """
        Kills the client process
        """

        kill_client_process()

    def send_command(self, command, value = None):
        """
        Send a command to the client process
        """
        if (self.state_alive):
            self.parent_conn.send([command, value])
        else:
            self.logger_conn.send(["err", "Client process dead."])

    def set_host(self, host):
        """
        Change the destination host
        """

        if (self.state_alive):
            self.parent_conn.send([STRCMD_LOOKUP['sethost'], host])
        else:
            self.logger_conn.send(["err", "Client process dead."])


    def set_port(self, port, is_tcp = True):
        """
        Change the destination port
        """

        if (self.state_alive):
            self.parent_conn.send([STRCMD_LOOKUP['setport'], port, is_tcp])
        else:
            self.logger_conn.send(["err", "Client process dead."])


    def kill_client_process(self):
        """
        Kill the process
        """

        if (self.state_alive):
            self.parent_conn.send([STRCMD_LOOKUP['killclient']])
            self.process.join()
        else:
            self.logger_conn.send(["err", "Client process dead."])

    def client_proc(self, client_host, client_tcp_port, client_udp_port, conn):
        # try init rover client
        try:
            self.logger_conn.send(["info", "Initializing client on {0}:{1}/{2}".format(client_host, client_tcp_port, client_udp_port)])
            client = RoverClient(host = client_host, tcp_port = client_tcp_port, udp_port = client_udp_port)
        except Exception as e:
            self.logger_conn.send(["err", "Error initializing rover client! {0}".format(e.message)])
            self.kill_flag = True

        # main loop
        while not self.kill_flag:
            try:
                msg = conn.recv()
        
                # Special commands which return values. TODO: should print value on GUI not console
                if (msg[0] == STRCMD_LOOKUP['ping']):
                    print client.ping()
                elif (msg[0] == STRCMD_LOOKUP['queryproc']):
                    print client.query()
                elif (msg[0] == STRCMD_LOOKUP['sensorinfo']):
                    print client.sensInfo()
    
                # Utility commands for the local client
                elif (msg[0] == STRCMD_LOOKUP['setport']):
                    client.setPort(msg[1], msg[2])
                elif (msg[0] == STRCMD_LOOKUP['sethost']):
                    client.setHost(msg[1])
    
                # Commands to kill the client and/or the server
                elif (msg[0] == STRCMD_LOOKUP['killclient']):
                    self.kill_flag = True
                elif (msg[0] == STRCMD_LOOKUP['graceful']):
                    client.sendCommand(msg[0])
                    self.kill_flag = True
    
                # Driving commands (timed & untimed)
                elif (msg[0] in range(0x07)):
                    client.timedCommand(msg[0], msg[1])
                        
                #Camera commands
                elif (msg[0] in range (0x20,0x24)):
                    client.sendCommand(msg[0])
    
                else:
                    raise Exception('Message type {0} not matched to a client message. Check clientproc.py').format(msg[0])
                self.logger_conn.send(["info", "Sent {0}".format(msg)])
            except Exception as e:
                self.logger_conn.send(["err", "Exception in station client process:\n{0}\nWaiting for next command.".format(e.message)])

        self.logger_conn.send(["info", "Client process on {0}:{1}/{2} terminated.".format(client_host, client_tcp_port, client_udp_port)])
        self.state_alive = False

