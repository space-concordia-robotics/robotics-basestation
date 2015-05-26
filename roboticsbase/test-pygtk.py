#!/usr/bin/env python2.7

import pygtk
pygtk.require('2.0')
import gtk

class Base:
    def click_me(self, widget, data=None):
        print "You clicked on me!"

    def delete_event(self, widget, event, data=None):
        print "delete event occured"
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        self.window.set_border_width(10)

        self.button = gtk.Button("Click ME!")
        self.button.connect("clicked", self.click_me, None)
      #  self.button.connect_object("clicked",
      #                             gtk.Widget.destroy,
      #                             self.window)

        self.window.add(self.button)
        self.button.show()
        self.window.show()
    
    def main(self):
        gtk.main()

print __name__

if __name__ == "__main__":
    base = Base()
    base.main()

