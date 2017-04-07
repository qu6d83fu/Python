from Tkinter import *
import urllib2

class kf_reloadGUI(Frame):
#	def __init__(self, master=None):
	def __init__(self, parent, controller):
#		Frame.__init__(self, master)
		Frame.__init__(self, parent)
		self.grid()
		self.createWidgets()
		self.controller = controller

	def createWidgets(self):
		self.button = Button(self, text="Home", command=lambda: self.controller.show_frame("StartPage"))
		self.button["width"]=30
		self.button.grid(row=0, column=0,columnspan=2)
     
		self.kf=Label(self)
		self.kf["text"] = "KF PORTAL"
		self.kf.grid(row=1, column=0,columnspan=2)
        
		self.trunkb = Button(self)
		self.trunkb["text"]="TRUNK"
		self.trunkb["width"]=15
		self.trunkb.grid(row=2, column=0,columnspan=1)
		self.trunkb["command"]=self.trunk

		self.server_twb = Button(self)
		self.server_twb["text"]="TW"
		self.server_twb["width"]=15
		self.server_twb.grid(row=2, column=1,columnspan=1)
		self.server_twb["command"]=self.server_tw

		self.server_cnb = Button(self)
		self.server_cnb["text"]="CN"
		self.server_cnb["width"]=15
		self.server_cnb.grid(row=3, column=0,columnspan=1)
		self.server_cnb["command"]=self.server_cn

		self.server_unb = Button(self)
		self.server_unb["text"]="UN"
		self.server_unb["width"]=15
		self.server_unb.grid(row=3, column=1,columnspan=1)
		self.server_unb["command"]=self.server_un

		
		self.portl=Label(self)
		self.portl["text"] = "Port "
		self.portl.grid(row=4, column=0,columnspan=1)
		self.portd = Entry(self)
		self.portd["width"]=15
		self.portd.grid(row=4, column=1,columnspan=1)


		self.reloadActivityb = Button(self)
		self.reloadActivityb["text"]="reloadActivity(G)"
		self.reloadActivityb["width"]=15
		self.reloadActivityb.grid(row=6, column=0,columnspan=1)
		self.reloadActivityb["command"]=self.reloadActivity


		self.publicinfob = Button(self)
		self.publicinfob["text"]="publicInfo refresh(P)"
		self.publicinfob["width"]=15
		self.publicinfob.grid(row=5, column=0,columnspan=1)
		self.publicinfob["command"]=self.publicInfo

		self.load_server_listb = Button(self)
		self.load_server_listb["text"]="load_server_list(P)"
		self.load_server_listb["width"]=15
		self.load_server_listb.grid(row=5, column=1,columnspan=1)
		self.load_server_listb["command"]=self.load_server_list

		self.reloadGiftEventb = Button(self)
		self.reloadGiftEventb["text"]="reloadGiftEvent(?)"
		self.reloadGiftEventb["width"]=15
		self.reloadGiftEventb.grid(row=6, column=1,columnspan=1)
		self.reloadGiftEventb["command"]=self.reloadGiftEvent


		self.message=Label(self)
		self.message["text"] = ""
		self.message["width"]=30
		self.message.grid(row=7, column=0,columnspan=2)

	def trunk(self):
		self.portd.delete(0, END)
		self.portd.insert(0,"45455")

	def server_tw(self):
		self.portd.delete(0, END)
		self.portd.insert(0,"45421")

	def server_cn(self):
		self.portd.delete(0, END)
		self.portd.insert(0,"45411")

	def server_un(self):
		self.portd.delete(0, END)
		self.portd.insert(0,"45423")

	def reload_url(self,path):
		self.message["text"] = ""
		self.port=int(self.portd.get())
		try:
			content = urllib2.urlopen("http://192.168.200.143:%s%s" %(self.port,path)).read()
			self.message["text"]= content
		except urllib2.HTTPError as u:
			self.message["text"]=str(u.code)+u.reason
			self.portd.delete(0, END)
		except urllib2.URLError as u:
			self.message["text"]="url error"
			self.portd.delete(0, END)

	def reloadActivity(self):
		self.reload_url("/backend/reloadActivity")

	def publicInfo(self):
		self.reload_url("/status/publicInfo_refresh")
			
	def load_server_list(self):
		self.reload_url("/login/load_server_list")

	def reloadGiftEvent(self):
		self.reload_url("/backend/reloadGiftEvent")