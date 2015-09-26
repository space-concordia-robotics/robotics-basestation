from common_constants import *
import threading

from roboticsnet.gateway_constants import ROBOTICSNET_PORT
from mjpg import VideoThread
import pygtk
pygtk.require('2.0')
import gtk
import urllib
import gobject
import threading

from joystick_listener import spawn_joystick_process



class BaseWindow:
    # Create the base window where all other items will be.
    def __init__(self):
        #this isn't necessary for gobject v~3+. not sure what the version being used is.
        gobject.threads_init()
        #main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", gtk.main_quit)
        self.window.set_default_size(500, 800)
        
        #video stream
        self.img = gtk.Image()
        self.img2 = gtk.Image()
        self.img.set_from_stock(gtk.STOCK_MISSING_IMAGE,gtk.ICON_SIZE_DIALOG)
        self.img2.set_from_stock(gtk.STOCK_MISSING_IMAGE,gtk.ICON_SIZE_DIALOG)
        self.img.show()
        self.img2.show()
        #widget that contains other widgets
        self.main_box=gtk.VBox()
        self.main_box.show()
        #buttons to go inside the widget widget
        self.button1 = gtk.Button("This is button1")
        self.button2 = gtk.Button("This is button2")

        self.widget_box = gtk.HBox(False, 0)
        self.video_box = gtk.HBox(False,0)

        self.video_box.pack_start(self.img)
        self.video_box.pack_start(self.img2)
        self.widget_box.pack_start(self.button1)    # test button
        self.widget_box.pack_start(self.button2)    # test button
        self.button1.set_size_request(400,30)
        self.button2.set_size_request(400,30)
        
        #exit button
        self.exit_button = gtk.Button(stock=gtk.STOCK_QUIT)
        self.exit_button.connect("clicked", self.destroy)
        self.exit_button.set_size_request(400,30)
        self.widget_box.pack_start(self.exit_button,fill=False)
        
        self.main_box.pack_start(self.video_box)
        self.main_box.pack_start(self.widget_box)
        self.window.add(self.main_box)
        self.window.show_all()


        # Used when closing window.
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        #creating video thread
        try:
            self.t = VideoThread(self.img)
            self.t2 = VideoThread(self.img2)
            self.t2.start()
            self.t.start()
        except:
            print "no video stream"

        
        #spawning joystick thread
        
        
        gtk.main()
        self.t.quit = True

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
   
    def main(self):
        # spawning joystick thread here for now. This functionality could be tied to a button/further integrated with the window
        # furthermore, events in e can be used in the window to trigger events
        e = [threading.Event() for i in range(NUM_BUTTON_EVENTS)]
        try:
            spawn_joystick_thread('localhost', ROBOTICSNET_PORT, e)
        except:
            print "no joystick connected"
        gtk.main()
