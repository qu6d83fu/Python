from Tkinter import *
import KF.reload
import ID.reload
import urllib2

TITLE_FONT = ("Helvetica", 12, "bold")
class SampleApp(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, KF.reload.kf_reloadGUI, ID.reload.id_reloadGUI):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="Select the game", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        button1 = Button(self, text="KF",width=20,height=2,bg="white",
                            command=lambda: controller.show_frame("kf_reloadGUI"))
        
        button2 = Button(self, text="ID",width=20,height=2,bg="white",
                            command=lambda: controller.show_frame("id_reloadGUI"))
        button1.pack()
        button2.pack()
        
		
if __name__ == "__main__":
#	root = Tk()
	#root.wm_title("reload_server")
#	app = CleanGUI(master=root)
    app = SampleApp()
    app.wm_title("reload_server")
    app.mainloop()