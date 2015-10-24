from common_constants import *
import threading
import sys, traceback

from roboticsnet.gateway_constants import ROBOTICSNET_PORT
from mjpg import VideoThread
import pygtk
pygtk.require('2.0')
import gtk
import urllib
import gobject
import threading
import multiprocessing
from send_command import send_locked_command
from roboticsnet.gateway_constants import *
from roboticsnet.roboticsnet_exception import RoboticsnetException
from roboticsnet.client.rover_client import RoverClient

from joystick_listener import spawn_joystick_process



class BaseWindow:
    # Create the base window where all other items will be.
    def __init__(self):
        self.lock = multiprocessing.Lock()
        self.client = RoverClient("localhost", 5000)
        self.isconnected = False
    
    
        #this isn't necessary for gobject v~3+. not sure what the version being used is.
        gobject.threads_init()
        self.lock = multiprocessing.Lock()


        ############################
        # Video Box
        ############################

        self.video_box = gtk.HBox(False,0)

        self.img = gtk.Image()
        self.img2 = gtk.Image()
        temp_img = gtk.gdk.pixbuf_new_from_file("TestMap.jpg")
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

        # Rescaling image
        image_test = gtk.Image()
        temp_image = gtk.gdk.pixbuf_new_from_file("TestMap.jpg")
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
        self.widget_box.attach(self.btn_video_show, 4, 5, 0, 1)

        # self.button1.set_size_request(100,30)
        # self.button2.set_size_request(100,30)
        # self.button3.set_size_request(100,30)
        # self.button4.set_size_request(100,30)

        # Movement
        self.btn_snapshot = gtk.Button("Snapshot")
        self.btn_panoramic = gtk.Button("Panoramic")
        self.btn_connect = gtk.Button("Connect")
        self.btn_connect.connect("clicked", self.connect)
        self.btn_right = gtk.Button("")

        self.ip_box = gtk.Entry(max=15)
        self.port_box = gtk.Entry(max=5)
        self.option_box = gtk.Entry(max=13)
        self.ip_box.set_text("IP")
        self.port_box.set_text("Port")
        self.option_box.set_text("Connect to...")

        self.widget_box.attach(self.btn_snapshot, 2, 3, 0, 1)
        self.widget_box.attach(self.btn_panoramic, 2, 3, 1, 2)
        self.widget_box.attach(self.btn_connect, 3, 4, 0, 1)
        self.widget_box.attach(self.btn_right, 3, 4, 1, 2)




        #exit button
        self.btn_exit = gtk.Button(stock=gtk.STOCK_QUIT)
        self.btn_exit.connect("clicked", self.destroy)
        # self.exit_button.set_size_request(100,30)

        self.widget_box.attach(self.btn_exit, 4, 5, 1, 2)



        ###########################
        # Status Box
        ###########################

        self.status_box = gtk.VBox(False, 0)
        text1 = gtk.TextView()
        text1.set_editable(False)

        text1_buffer = text1.get_buffer()
        text1_buffer.set_text("Testing!!!!!")

        self.status_box.pack_start(text1)
        
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
        #self.window.set_default_size(1500, 2000)
        self.window.set_size_request(1200, 700)

        self.window.set_resizable(False)
        self.window.set_title("Basestation")
        self.window.set_position(gtk.WIN_POS_CENTER)

        # Containers
        self.main_box = gtk.VBox()
        self.main_box.show()

        self.top_container = gtk.Table(2,3)
        self.top_container.attach(self.image_box, 0, 1, 1, 2)
        self.top_container.attach(self.video_box, 0, 2, 0, 1)
        self.top_container.attach(self.status_box, 1, 2, 1, 2)
        self.top_container.attach(self.entry_box, 1, 2, 2, 3)


        self.main_box.pack_start(self.top_container)
        self.main_box.pack_start(self.widget_box)

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

        if response == gtk.RESPONSE_YES:
            md.destroy()
            self.destroy(self, widget)
            return False
        else:
            md.destroy()
            return True

    def destroy(self, widget, data=None):
        gtk.main_quit()
        
    def start_video(self, event):
        try:
            self.sendcommand(ROBOTICSNET_COMMAND_START_VID)
        except:
            print "cannot start video"
            traceback.print_exc(file=sys.stdout)
            
        
    def stop_video(self, event):
        try:
            self.sendcommand(ROBOTICSNET_COMMAND_STOP_VID)
        except:
            print "cannot stop video"
    
    def show_video(self, event):
        try:
            self.t = VideoThread(self.img,self.ip_box.get_text(),self.port_box.get_text())
            self.t2 = VideoThread(self.img2,self.ip_box.get_text(),self.port_box.get_text())
            self.t2.start()
            self.t.start()
        except:
            print "no video stream"
            traceback.print_exc(file=sys.stdout)
    
    def quit_video(self, event):
        try:
            self.t.quit = True
            self.t2.quit = True
        except:
            print "no video stream to quit"
    
    
    def stop_joystick(self, event):
        try:
            events[ROBOTICSBASE_STOP_LISTENER].set()
        except:
            print "cannot stop joystick thread"
    
    def start_joystick(self, event):
        try:
            spawn_joystick_thread('localhost', ROBOTICSNET_PORT, e)
        except:
            print "no joystick connected"
    
    def print_text(self, text):
        pass

    def sendcommand(self, command):
        command_process = multiprocessing.Process(target = send_locked_command, args=(self.client, self.lock, command, 0))
        command_process.start()
        
    def connect(self):
        if "server" in option_box.get_text().lower():
            self.client.setHost(self.ip_box.get_text())
            self.client.setPort(int(self.port_box.get_text()))
        elif "1" in option_box.get_text().lower():
            pass
        elif "2" in option_box.get_text().lower():
            pass
        else:
            option_box.set_text("Invalid option")
   
    def main(self):
        # spawning joystick thread here for now. This functionality could be tied to a button/further integrated with the window
        # furthermore, events in e can be used in the window to trigger events
        e = [threading.Event() for i in range(NUM_BUTTON_EVENTS)]
        gtk.main()


if __name__ == "__main__":
    base = BaseWindow()
