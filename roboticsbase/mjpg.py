import pygtk
pygtk.require('2.0')
import gtk
import urllib
import gobject
import threading


class VideoThread(threading.Thread):
    '''
    A background thread that takes the MJPEG stream and
    updates the GTK image.
    '''
    def __init__(self, widget, streamip, streamport):
        super(VideoThread, self).__init__()
        self.widget = widget
        self.quit = False
        self.streamip = streamip
        self.streamport = streamport
        self.STREAM_URL = 'http://'+streamip+":"+streamport+"/?action=stream"
        print 'connecting to', self.STREAM_URL
        self.stream = urllib.urlopen(self.STREAM_URL)

    def get_raw_frame(self):
        '''
        Parse an MJPEG http stream and yield each frame.
        Source: http://stackoverflow.com/a/21844162

        :return: generator of JPEG images
        '''
        raw_buffer = ''
        while True:
            new = self.stream.read(1034)
            if not new:
                # Connection dropped
                yield None
            raw_buffer += new
            a = raw_buffer.find('\xff\xd8')
            b = raw_buffer.find('\xff\xd9')
            if a != -1 and b != -1:
                frame = raw_buffer[a:b+2]
                raw_buffer = raw_buffer[b+2:]
                yield frame

    def run(self):
        for frame in self.get_raw_frame():
            if self.quit or frame is None:
                return
            loader = gtk.gdk.PixbufLoader('jpeg')
            loader.write(frame)
            loader.close()
            pixbuf = loader.get_pixbuf()
            # Schedule image update to happen in main thread
            gobject.idle_add(self.widget.set_from_pixbuf, pixbuf)



