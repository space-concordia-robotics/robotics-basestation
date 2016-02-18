from multiprocessing import Process, Event

class TextBuffer():
    """
    This class manages a text box and writes messages asynchronously that are passed
    through a multiprocessing pipe. Similar to logger class except using the GTK 
    text buffer.
    """

    def __init__(self, text_buffer, pipe_recv, pipe_send):
        """
        text_box:
            The GTK text box object whose buffer is being written to.

        message_pipe:
            The multiprocessing pipe through which messages are received.
        """

        self.text_buffer = text_buffer
        self.pipe_recv = pipe_recv
        self.pipe_send = pipe_send
        self.alive = True

        self.proc = Process(target=self.run, args=(self.text_buffer, self.pipe_recv))
        self.proc.start()

    def __del__(self):
        """
        Kill the text buffer manager
        """

        send_kill()

    def send_kill(self):
        """
        Send a kill message to the process
        """

        self.pipe_send.send(['kill'])

    def run(self, text_buffer, pipe):
        """
        Thread logic
        """

        while True:
            msg = pipe.recv()
            print msg

            if (msg[0] == 'insert'):
                text_buffer.set_text(msg[1])
            elif (msg[0] == 'kill'):
                break
