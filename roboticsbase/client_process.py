from roboticsnet.gateway_constants import *

from roboticsnet.roboticsnet_exception import RoboticsnetException
from roboticsnet.rover_client import RoverClient
from roboticslogger.logger import Logger
from multiprocessing import Process, Pipe
import socket
import sys

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

    def __init__(self, logger_conn, message_conn):
        """
        Initializes a rover client process on host:port
        """

        self.kill_flag = False
        self.state_alive = True
        self.logger_conn = logger_conn
        self.proc_send_conn, proc_recv_conn = Pipe()
        self.process = Process(target=self.client_proc,
                args=(proc_recv_conn, message_conn))
        self.process.start()

    def __del__(self):
        """
        Kills the client process
        """

        kill_client_process()

    def send_command(self, command, value = 0):
        """
        Send a command to the client process
        """
        if (self.state_alive):
            self.proc_send_conn.send([command, value])
        else:
            self.logger_conn.send(["err", "Client process dead."])

    def kill_client_process(self):
        """
        Kill the process
        """

        if (self.state_alive):
            self.proc_send_conn.send([CLIENT_KILL])
            self.process.join()
        else:
            self.logger_conn.send(["err", "Client process dead."])

    def client_proc(self, recv_conn, send_conn):
        """
        Client process logic loop
        """

        # try init rover client
        try:
            self.logger_conn.send(["info", "Initializing client"])
            client = RoverClient()
        except Exception as e:
            self.logger_conn.send(["err", "Error initializing rover client! {0}".format(e.message)])
            self.kill_flag = True

        # main loop
        while not self.kill_flag:
            try:
                msg = recv_conn.recv()

                # Special commands which return values. TODO: should print value on GUI not console
                if (msg[0] == SYSTEM_PING):
                    time = client.ping()
                    if time==None:
                        send_conn.send("No connection")
                    else:
                        send_conn.send("Ping returned in {0}s".format(time))
                elif (msg[0] == SYSTEM_QUERYPROC):
                    send_conn.send(client.query())
                elif (msg[0] == SENSOR_INFO):
                    send_conn.send(client.sensInfo())
                elif (msg[0] == CAMERA_SNAPSHOT or msg[0] == CAMERA_PANORAMIC):
                    pass
                    #send_conn.send(client.snapshot(msg[0]))

                # Commands to kill the client and/or the server
                elif (msg[0] == CLIENT_KILL):
                    self.kill_flag = True
                elif (msg[0] == SYSTEM_GRACEFUL):
                    client.sendCommand(msg[0])
                    self.kill_flag = True

                # Driving commands (timed & untimed)
                elif (msg[0] in range(0x05)):
                    client.timedCommand(msg[0], msg[1])
                    print "Driving with {0}:{1}".format(msg[0], msg[1])

                #Camera commands
                elif (msg[0] == CAMERA_START_VID or msg[0] == CAMERA_STOP_VID):
                    client.sendCommand(msg[0])

                else:
                    raise Exception("Message type {0} not matched to a client message. Check clientproc.py".format(msg[0]))
                self.logger_conn.send(["info", "Sent {0}".format(msg)])
            except:
                self.logger_conn.send(["err", "Exception in station client process. Waiting for next command."])

        self.logger_conn.send(["info", "Client process terminated."])
        self.state_alive = False

