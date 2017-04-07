from Tkinter import *
import urllib2

class id_reloadGUI(Frame):
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
		self.button.grid(row=0, column=0, columnspan=2)

		self.kf=Label(self)
		self.kf["text"] = "ID PORTAL"
		self.kf.grid(row=1, column=0, columnspan=2)        

		self.trunkb = Button(self)
		self.trunkb["text"]="TRUNK"
		self.trunkb["width"]=15
		self.trunkb.grid(row=2, column=0)
		self.trunkb["command"]=self.trunk

		self.serverb = Button(self)
		self.serverb["text"]="SERVER"
		self.serverb["width"]=15
		self.serverb.grid(row=2, column=1)
		self.serverb["command"]=self.server



		self.portl=Label(self)
		self.portl["text"] = "Port "
		self.portl.grid(row=3, column=0)
		self.portd = Entry(self)
		self.portd["width"]=15
		self.portd.grid(row=3, column=1, columnspan=5)


		self.reloadActivityb = Button(self)
		self.reloadActivityb["text"]="refreshActivityQuestAll(Game)"
		self.reloadActivityb["width"]=30
		self.reloadActivityb.grid(row=4, column=0, columnspan=2)
		self.reloadActivityb["command"]=self.refreshActivityQuestAll


		self.publicinfob = Button(self)
		self.publicinfob["text"]="refresh_DB_RewardList(Game)"
		self.publicinfob["width"]=30
		self.publicinfob.grid(row=5, column=0, columnspan=2)
		self.publicinfob["command"]=self.refresh_DB_RewardList

		self.load_server_listb = Button(self)
		self.load_server_listb["text"]="loadPublicInfo(Portal)"
		self.load_server_listb["width"]=30
		self.load_server_listb.grid(row=6,  columnspan=2)
		self.load_server_listb["command"]=self.loadPublicInfo
		self.message=Label(self)
		self.message["text"] = ""
		self.message["width"]= 30
		self.message.grid(row=7, column=0,columnspan=2)

	def trunk(self):
		self.portd.delete(0, END)
		self.portd.insert(0,"44100")

	def server(self):
		self.portd.delete(0, END)
		self.portd.insert(0,"44000")


	def reload_url(self,path):
		self.message["text"] = ""
		self.port=int(self.portd.get())
		try:
			content = urllib2.urlopen("http://192.168.200.145:%s%s" %(self.port,path)).read()
			self.message["text"]= content
		except urllib2.HTTPError as u:
			self.message["text"]=str(u.code)+u.reason
			self.portd.delete(0, END)
		except urllib2.URLError as u:
			self.message["text"]="url error"
			self.portd.delete(0, END)

	def refreshActivityQuestAll(self):
		self.reload_url("/backend/refreshActivityQuestAll")

	def refresh_DB_RewardList(self):
		self.reload_url("/backend/refresh_DB_RewardList")
			
	def loadPublicInfo(self):
		self.reload_url("/status/loadPublicInfo")
