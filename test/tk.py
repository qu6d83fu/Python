from Tkinter import *
#from Tkinter.ttk import *
#root = Tk()
#text = Label(root, text = "Tk's job!!",
#			width ="80", height="50",
#			bg = "black", fg = "white")

#text.pack()
#root.mainloop()

class EncryptGUI(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.grid()
		self.createWidgets()

	def createWidgets(self):
		self.it=Label(self)
		self.it["text"] = "Input: "
		self.it.grid(row=0, column=0)
		self.ifd = Entry(self)
		self.ifd["width"]=60
		self.ifd.grid(row=0, column=1, columnspan=6)

		self.ot=Label(self)
		self.ot["text"] = "Output: "
		self.ot.grid(row=1, column=0)
		self.ofd = Entry(self)
		self.ofd["width"]=60
		self.ofd.grid(row=1, column=1, columnspan=6)

		self.nb = Button(self)
		self.nb["text"] = "New"
		self.nb.grid(row=2, column=0)
		self.nb["command"]=self.nm

		self.lb = Button(self)
		self.lb["text"] ="Load"
		self.lb.grid(row=2, column=1)
		self.lb["command"]=self.lm

		self.sb = Button(self)
		self.sb["text"] = "Save"
		self.sb.grid(row=2, column=2)
		self.sb["command"]=self.sm

		self.eb = Button(self)
		self.eb["text"] = "Encode"
		self.eb.grid(row=2, column=3)
		self.eb["command"]=self.em

		self.db = Button(self)
		self.db["text"]= "Decode"
		self.db.grid(row=2, column=4)
		self.db["command"]=self.dm

		self.cb = Button(self)
		self.cb["text"]="Clear"
		self.cb.grid(row=2, column=5)
		self.cb["command"]=self.cm

		self.cb2 = Button(self)
		self.cb2["text"]="Copy"
		self.cb2.grid(row=2, column=6)
		self.cb2["command"]=self.cm2

		self.dt=Label(self)
		m="something happend"
		self.dt["text"]=m
		self.dt.grid(row=3, column=0, columnspan=7)

	def nm(self):
		a=int(self.ifd.get())+int(self.ofd.get())
		self.dt["text"]=a

	def lm(self):
		self.dt["text"]="Load Button"

	def sm(self):
		self.dt["text"]="Save Button"

	def em(self):
		self.dt["text"]="Encode Button"

	def dm(self):
		self.dt["text"]="Decode Button"

	def cm(self):
		self.dt["text"]="Clear Button"

	def cm2(self):
		self.dt["text"]="Copy Button"

if __name__ == "__main__":
	root = Tk()
	app = EncryptGUI(master=root)
	app.mainloop()