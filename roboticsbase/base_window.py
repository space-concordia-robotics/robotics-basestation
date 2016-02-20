import threading
import sys, traceback
import pygtk
pygtk.require('2.0')
import gtk
import urllib
import gobject
import threading
import multiprocessing
import os

from roboticslogger.logger import Logger
from roboticsnet.gateway_constants import *
from common_constants import *
from mjpg import VideoThread
from roboticsnet.roboticsnet_exception import RoboticsnetException
from client_process import ClientProcess
from joystick_listener import spawn_joystick_process

class BaseWindow:
    # Create the base window where all other items will be.
    def __init__(self):
        # Logger
        self.logger = Logger("basestation")
        self.logger_parent_conn, self.logger_child_conn = multiprocessing.Pipe()
        self.p = multiprocessing.Process(target=self.logger.run, args = (self.logger_child_conn, ))
        self.p.start()

        self.e = [multiprocessing.Event() for i in range(ROBOTICSBASE_NUM_EVENTS)]
        self.cproc_send, self.cproc_recv = multiprocessing.Pipe()
        self.client = ClientProcess("localhost", 10666, 10667,
                self.logger_parent_conn, self.cproc_send)
        self.isconnected = False

        # this isn't necessary for gobject v~3+. not sure what the version being used is.
        gobject.threads_init()

        ############################
        # Video Box
        ############################

        self.video_box = gtk.HBox(False,0)

        self.img = gtk.Image()
        self.img2 = gtk.Image()

        self.img.set_from_stock(gtk.STOCK_MISSING_IMAGE,gtk.ICON_SIZE_DIALOG)
        self.img2.set_from_stock(gtk.STOCK_MISSING_IMAGE,gtk.ICON_SIZE_DIALOG)
        self.img.show()
        self.img2.show()


        self.video_box.pack_start(self.img)
        self.video_box.pack_start(self.img2)

        ############################
        # Image Box
        ############################

        self.image_box = gtk.Fixed()
        directory = os.path.dirname("TestMap.jpg")
        path = os.path.abspath(os.path.dirname(__file__))
        temp_image = gtk.gdk.pixbuf_new_from_file(os.path.join(path,"TestMap.jpg"))
        # Rescaling image
        image_test = gtk.Image()
        scaled_image = temp_image.scale_simple(400, 300, gtk.gdk.INTERP_BILINEAR)
        image_test.set_from_pixbuf(scaled_image)

        self.image_box.put(image_test, 0, 0)

        rover_icon = gtk.Image()
        rover_icon.set_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_BUTTON)

        self.image_box.put(rover_icon, 50, 50)



        ###########################
        # Control Widgets Box
        ###########################

        self.widget_box = gtk.Table(5, 2)

        #buttons for starting and stopping the joystick listener

        self.btn_stick_start = gtk.Button("(Re)start joystick listener")
        self.btn_stick_stop = gtk.Button("Stop joystick listener")
        self.btn_stick_start.connect("clicked",self.start_joystick)
        self.btn_stick_stop.connect("clicked",self.stop_joystick)

        self.widget_box.attach(self.btn_stick_start, 0, 1, 0, 1)
        self.widget_box.attach(self.btn_stick_stop, 0, 1, 1, 2)

        #buttons for starting and stopping the video stream
        self.btn_video_start = gtk.Button("Start video stream")
        self.btn_video_start.connect("clicked",self.start_video)
        self.btn_video_stop = gtk.Button("Stop video stream")
        self.btn_video_stop.connect("clicked",self.stop_video)
        self.btn_video_show = gtk.Button("Show video stream")
        self.btn_video_show.connect("clicked",self.show_video)
        self.widget_box.attach(self.btn_video_start, 1, 2, 0, 1)
        self.widget_box.attach(self.btn_video_stop, 1, 2, 1, 2)
        self.widget_box.attach(self.btn_video_show, 2, 3, 0, 1)

        # Movement
        self.btn_snapshot = gtk.Button("Snapshot")
        self.btn_snapshot.connect("clicked", self.snapshot)
        self.btn_panoramic = gtk.Button("Panoramic")
        self.btn_panoramic.connect("clicked",self.panoramic)
        self.btn_connect = gtk.Button("Connect")
        self.btn_connect.connect("clicked", self.connect)
        self.btn_quit_video = gtk.Button("Stop Video Thread")
        self.btn_quit_video.connect("clicked",self.quit_video)

        self.ip_box = gtk.Entry(max=15)
        self.port_box = gtk.Entry(max=5)
        self.option_box = gtk.Entry(max=25)
        self.ip_box.set_text("192.168.1.201")
        self.port_box.set_text("5000")
        self.option_box.set_text("Connect to server")

        self.widget_box.attach(self.btn_snapshot, 3, 4, 0, 1)
        self.widget_box.attach(self.btn_panoramic, 3, 4, 1, 2)
        self.widget_box.attach(self.btn_connect, 4, 5, 0, 1)
        self.widget_box.attach(self.btn_quit_video, 2, 3, 1, 2)




        #exit button
        self.btn_exit = gtk.Button(stock=gtk.STOCK_QUIT)
        self.btn_exit.connect("clicked", self.destroy)

        self.widget_box.attach(self.btn_exit, 4, 5, 1, 2)



        ###########################
        # Status Box
        ###########################

        self.status_box = gtk.HBox(False, 0)
        self.text1 = gtk.TextView()
        self.text1.set_editable(False)
        self.text1_buffer = self.text1.get_buffer()

        self.text1_buffer.set_text("GUI started.")

        self.status_box.pack_start(self.text1)

        self.entry_box = gtk.VBox(False,0)
        self.entry_box.pack_start(self.ip_box)
        self.entry_box.pack_start(self.port_box)
        self.entry_box.pack_start(self.option_box)

        ###########################
        # Main window things
        ###########################



        # Initialize window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", gtk.main_quit)
        self.window.set_size_request(1200, 700)

        self.window.set_resizable(True)
        self.window.set_title("Basestation")
        self.window.set_position(gtk.WIN_POS_CENTER)

        # Containers
        self.main_box = gtk.VBox()
        self.main_box.show()

        self.top_container = gtk.Table(3,6)
        self.top_container.attach(self.image_box, 0, 1, 4, 5)
        self.top_container.attach(self.video_box, 0, 3, 0, 4)
        self.top_container.attach(self.status_box, 1, 2, 4, 5)
        self.top_container.attach(self.entry_box, 2, 3, 4, 5)
        self.top_container.attach(self.widget_box, 0, 4, 5, 6)


        self.main_box.pack_start(self.top_container)

        self.window.add(self.main_box)
        self.window.show_all()


        ###########################
        # Miscellaneous
        ###########################s

        # Used when closing window.
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)


        gtk.main()

    def delete_event(self, widget, event, data=None):
        msg = "Are you sure you want to quit?"
        md = gtk.MessageDialog(self.app_window,
                               gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_QUESTION,
                               gtk.BUTTONS_YES_NO,
                               msg)
        md.set_title("Quit the program?")

        response = md.run()
        self.logger_parent_conn.send(["info", "closing base window"])
        if response == gtk.RESPONSE_YES:
            md.destroy()
            self.destroy(self, widget)
            return False
        else:
            md.destroy()
            return True

    def destroy(self, widget, data=None):
        self.client.kill_client_process()
        self.logger_parent_conn.send(["done"])
        gtk.main_quit()

    def start_video(self, event):
        try:
            self.client.send_command(ROBOTICSNET_CAMERA_START_VID)
            self.logger_parent_conn.send(["info", "starting video stream"])
        except:
            self.logger_parent_conn.send(["err", "cannot start video"])
            traceback.print_exc(file=sys.stdout)


    def stop_video(self, event):
        try:
            self.client.send_command(ROBOTICSNET_CAMERA_STOP_VID)
            self.logger_parent_conn.send(["info", "stopping video stream"])
        except:
            print "cannot stop video"

    def show_video(self, event):
        try:
            self.t = VideoThread(self.img,self.ip_box.get_text(),self.port_box.get_text())
            self.t2 = VideoThread(self.img2,self.ip_box.get_text(),self.port_box.get_text())
            self.t2.start()
            self.t.start()
            self.logger_parent_conn.send(["info", "displaying video"])
        except:
            self.logger_parent_conn.send(["err", "cannot find stream"])
            self.logger_parent_conn.send(["err", sys.exc_info()[0]])

    def quit_video(self, event):
        try:
            self.t.quit = True
            self.t2.quit = True
            self.logger_parent_conn.send(["info", "stopping video display"])
        except:
            print "no video stream to quit"


    def stop_joystick(self, event):
        try:
            self.e[ROBOTICSBASE_STOP_LISTENER].set()
            self.logger_parent_conn.send(["info", "stopping joystick listener"])
        except:
            self.logger_parent_conn.send(["err", "cannot stop joystick thread. probably doesn't exist"])

    def start_joystick(self, event):
        try:
            spawn_joystick_process(self.client, self.e)
            self.logger_parent_conn.send(["info", "starting joystick listener"])
        except:
            self.logger_parent_conn.send(["err", "cannot start joystick listener. It's almost definitely because there isn't one connected"])

    def print_text(self, text):
        """
        Prints text to be displayed on the GUI (whichever way you prefer that to happen)
        """
        self.text1_buffer.set_text(text)
        pass

    def snapshot(self, event):
        self.logger_parent_conn.send(["info", "Taking a snapshot"])
        pass

    def panoramic(self, event):
        self.logger_parent_conn.send(["info", "Taking a panoramic"])
        pass

    def send_await_response(self, command):
        self.client.send_command(command)
        return self.cproc_recv.recv()

    def connect(self, event):

        if "server" in self.option_box.get_text().lower():
            self.client.set_host(self.ip_box.get_text())
            self.client.set_port(int(self.port_box.get_text()), True)

            self.logger_parent_conn.send(["info", "Basestation trying to ping server..."])
            self.print_text(self.send_await_response(ROBOTICSNET_SYSTEM_PING))
        elif "1" in self.option_box.get_text().lower():
            self.logger_parent_conn.send(["info", "Basestation trying to connect to first video stream"])
        elif "2" in self.option_box.get_text().lower():
            self.logger_parent_conn.send(["info", "basestation connecting to video stream 2"])
            pass
        else:
            self.option_box.set_text("Invalid option")

    def main(self):
        # spawning joystick thread here for now. This functionality could be tied to a button/further integrated with the window
        # furthermore, events in e can be used in the window to trigger events
        gtk.main()


if __name__ == "__main__":
    base = BaseWindow()
