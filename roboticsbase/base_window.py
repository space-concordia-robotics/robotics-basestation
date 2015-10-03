from common_constants import *
import threading

from roboticsnet.gateway_constants import ROBOTICSNET_PORT
try:
    from mjpg import VideoThread
except:
    print ""
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
    
    
        #this isn't necessary for gobject v~3+. not sure what the version being used is.
        gobject.threads_init()
        self.lock = multiprocessing.Lock()
        #main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", gtk.main_quit)
        self.window.set_default_size(500, 800)

        #video stream
        self.img = gtk.Image()
        self.img2 = gtk.Image()
        self.img.set_from_stock(gtk.STOCK_MISSING_IMAGE,gtk.ICON_SIZE_DIALOG)
        self.img2.set_from_stock(gtk.STOCK_MISSING_IMAGE,gtk.ICON_SIZE_DIALOG)
        self.img.set_size_request(600,500)
        self.img2.set_size_request(600,500)
        self.img.show()
        self.img2.show()
        #widget that contains other widgets
        self.main_box=gtk.VBox()
        self.main_box.show()
        #buttons for starting and stopping the joystick listener
        self.joystick_buttons = gtk.VBox()

        self.button1 = gtk.Button("(Re)start joystick listener")
        self.button2 = gtk.Button("Stop joystick listener")
        self.button1.connect("clicked",self.start_joystick)
        self.button2.connect("clicked",self.stop_joystick)
        #self.textbox = GtkText(None, None)
        self.joystick_buttons.pack_start(self.button1)
        self.joystick_buttons.pack_start(self.button2)
        #self.joystick_buttons.pack_start(self.textbox)
        #self.textbox.set_editable(editable)
        #self.textbox.set_word_wrap(word_wrap)
        #elf.textbox.set_point(0)
        #elf.textbox.insert_defaults(string)
        #res = self.textbox.backward_delete(self.textbox.get_length())
        
        #buttons for starting and stopping the video stream
        self.video_buttons = gtk.VBox()
        self.button3 = gtk.Button("(Re)start video stream")
        self.button3.connect("clicked",self.start_video)
        self.button4 = gtk.Button("Stop video stream")
        self.button4.connect("clicked",self.stop_video)
        self.button5 = gtk.Button("Show video")
        self.button5.connect("clicked",self.show_video)
        self.joystick_buttons.pack_start(self.button3)
        self.joystick_buttons.pack_start(self.button4)
        self.joystick_buttons.pack_start(self.button5)
        
        self.textboxes = gtk.HBox()
        self.ipbox = gtk.Entry(max=15)
        self.portbox = gtk.Entry(max=5)
        self.ipbox.text = "Stream IP"
        self.ipbox.show()
        self.portbox.text = "Stream Port"
        self.portbox.show()
        self.exit_button = gtk.Button(stock=gtk.STOCK_QUIT)
        self.exit_button.connect("clicked", self.destroy)
        self.exit_button.set_size_request(200,30)
        self.joystick_buttons.pack_start(self.exit_button)
        self.joystick_buttons.pack_start(self.ipbox)
        self.joystick_buttons.pack_start(self.portbox)


        self.widget_box = gtk.HBox(False, 0)
        self.video_box = gtk.HBox(False,0)

        self.video_box.pack_start(self.img)
        self.video_box.pack_start(self.img2)
        self.widget_box.pack_start(self.joystick_buttons)    # test button
        self.widget_box.pack_start(self.video_buttons)    # test button
        self.button1.set_size_request(400,30)
        self.button2.set_size_request(400,30)

        self.button3.set_size_request(400,30)
        self.button4.set_size_request(400,30)
        self.button5.set_size_request(400,30)
        #exit button



        self.main_box.pack_start(self.video_box)
        self.main_box.pack_start(self.widget_box)
        self.main_box.pack_start(self.textboxes)
        self.window.add(self.main_box)
        self.window.show_all()


        # Used when closing window.
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        #creating video thread



        #spawning joystick thread


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
        try:
            self.t.quit = True
            self.t2.quit = True
        except:
            print "no video stream to quit"
        gtk.main_quit()

    def show_video(self, event):
        try:
            self.t = VideoThread(self.img,self.ipbox.text,self.portbox.text)
            self.t2 = VideoThread(self.img2,self.ipbox.text,self.portbox.text)
            self.t2.start()
            self.t.start()
        except:
            print "no video stream"
            
    
    def start_video(self, event):
        try:
            sendcommand(ROBOTICSNET_COMMAND_STOP_VID)
            sendcommand(ROBOTICSNET_COMMAND_START_VID)
        except:
            print "cannot start video"
        
        
    def stop_video(self, event):
        try:
            sendcommand(ROBOTICSNET_COMMAND_STOP_VID)
        except:
            print "cannot stop video"

    def stop_joystick(self, event):
        try:
            events[ROBOTICSBASE_STOP_LISTENER].set()
        except:
            print "cannot stop joystick thread"
    
    def start_joystick(self, event):
        try:
            events[ROBOTICSBASE_STOP_LISTENER].set()
            spawn_joystick_thread('localhost', ROBOTICSNET_PORT, e)
        except:
            print "no joystick connected"
    
    def print_text(self, text):
        pass

    def sendcommand(command):
        command_process = multiprocessing.Process(target = send_locked_command, args=(self.client, self.lock, command, 0))
        command_process.start() 

   
    def main(self):
        # spawning joystick thread here for now. This functionality could be tied to a button/further integrated with the window
        # furthermore, events in e can be used in the window to trigger events
        e = [threading.Event() for i in range(NUM_BUTTON_EVENTS)]
        gtk.main()
