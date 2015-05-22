__version__ = '0.0.1'

#!/usr/bin/python

class HomeGui:
    import Tkinter
    outer = Tkinter.Tk()

    root = Tkinter.PanedWindow(outer, orient = "vertical")
    root.pack()

    photo = Tkinter.PhotoImage(file="images/RecordImage.gif")
    video = Tkinter.Label(outer, image = photo)
    video.pack()
    root.add(video)

    photo2 = Tkinter.PhotoImage(file="images/map-and-compass.gif", height=200)
    video2 = Tkinter.Label(outer, image = photo2)
    video2.pack()
    root.add(video2)

    message = Tkinter.Text(outer)
    message.insert("1.0", "Hello")
    message.pack()
    root.add(message)
    
    outer.mainloop()
    

    
