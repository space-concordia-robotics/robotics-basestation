from common_constants import *
import threading
from controller import listenjoystick



class BaseWindow:
    # Create the base window where all other items will be.
    def __init__(self):
        self.app_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.app_window.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.app_window.set_border_width(WINDOW_BORDER_WIDTH)
        self.app_window.set_title(WINDOW_TITLE)
        self.app_window.set_position(gtk.WIN_POS_CENTER)

        ############################
        # Video Box
        ############################

        # add video widgets here


        self.video_box = gtk.HBox()
        
        ############################
        # Status Box
        ############################

        # add status widgets here
        # self.web = webkit.WebView()
        # self.web.open("www.google.ca")
        # self.map = gtk.Frame('Maps')
        # self.scroll = gtk.ScrolledWindow()
        # self.scroll.add(self.web)
        # self.map.add(self.scroll)
        
        self.status_box = gtk.HBox()
        # self.status_box.pack_start(self.map)

        ############################
        # Control Widgets Box 
        ############################
        
        # Exit button
        self.exit_button = gtk.Button(stock=gtk.STOCK_QUIT)
        self.exit_button.connect("clicked", self.destroy)

        self.button1 = gtk.Button("This is button1")
        self.button2 = gtk.Button("This is button2")

        self.widget_box = gtk.HBox(False, 0)
        self.widget_box.pack_start(self.button1)    # test button
        self.widget_box.pack_start(self.button2)    # test button
        self.widget_box.pack_start(self.exit_button)


        ###########################
        # Main window stuff
        ##########################

        # Put all box into the main one.
        self.main_box = gtk.VBox()
        self.main_box.pack_start(self.video_box)
        self.main_box.pack_start(self.status_box)
        self.main_box.pack_start(self.widget_box)

        # Show everything in window
        self.app_window.add(self.main_box)
        self.app_window.show_all()

        # Used when closing window.
        self.app_window.connect("delete_event", self.delete_event)
        self.app_window.connect("destroy", self.destroy)

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
        t = threading.Thread(target=listenjoystick, args=())
        t.start()
        gtk.main()


