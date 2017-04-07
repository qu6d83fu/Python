from Tkinter import *
import mysql.connector
from datetime import date, datetime, timedelta


class InfoGUI(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.grid()
		self.createWidgets()

	def createWidgets(self):
		self.name=Label(self)
		self.name["text"] = "Name: "
		self.name.grid(row=0, column=0)
		self.named = Entry(self)
		self.named["width"]=10
		self.named.grid(row=0, column=1)

		self.birth=Label(self)
		self.birth["text"] = "Birthday: "
		self.birth.grid(row=0, column=2)
		self.birthd = Entry(self)
		self.birthd["width"]=10
		self.birthd.grid(row=0, column=3)

		self.id=Label(self)
		self.id["text"] = "Identification: "
		self.id.grid(row=1, column=0)
		self.idd = Entry(self)
		self.idd["width"]=10
		self.idd.grid(row=1, column=1)

		self.phone=Label(self)
		self.phone["text"] = "Phone: "
		self.phone.grid(row=1, column=2)
		self.phoned = Entry(self)
		self.phoned["width"]=10
		self.phoned.grid(row=1, column=3)


		self.addr=Label(self)
		self.addr["text"] = "address: "
		self.addr.grid(row=2, column=0, )
		self.addrd = Entry(self)
		self.addrd["width"]=30
		self.addrd.grid(row=2, column=1, columnspan=4)

		self.insert = Button(self)
		self.insert["text"]="Insert"
		self.insert["width"]=8
		self.insert.grid(row=3, column=0)
		self.insert["command"]=self.insertb

		self.update = Button(self)
		self.update["text"]="Update"
		self.update["width"]=8
		self.update.grid(row=3, column=1)
		self.update["command"]=self.updateb

		self.delete = Button(self)
		self.delete["text"]="delete"
		self.delete["width"]=8
		self.delete.grid(row=3, column=2)
		self.delete["command"]=self.deleteb

		self.query = Button(self)	
		self.query["text"]="query"
		self.query["width"]=8
		self.query.grid(row=3, column=3)
		self.query["command"]=self.queryb

		self.message=Label(self)
		self.message["text"] = ""


		self.message.grid(row=4, column=0,columnspan=300)

	def insertdata(self,a,b,c,d,e):
		cnx = mysql.connector.connect(user='neil', password='neil',
                              host='52.193.112.188',
                              database='python')
		cursor = cnx.cursor()
		tomorrow = datetime.now().date() + timedelta(days=1)
		add_info = ("INSERT INTO  information "
               "(Name, Birthday, Identification, Phone, Address) "
               "VALUES (%s, %s, %s, %s, %s)")

		data_info = (a,b,c,d,e)
		cursor.execute(add_info, data_info)
		cnx.commit()
		cursor.close()
		cnx.close()

	def updatedata(self,a,b,c,d,e):
		cnx = mysql.connector.connect(user='neil', password='neil',
                              host='52.193.112.188',
                              database='python')
		cursor = cnx.cursor()
		tomorrow = datetime.now().date() + timedelta(days=1)
		add_info = ("update information set Name = %s, Birthday = %s, Identification = %s, Phone = %s, Address = %s where Name = %s")

		data_info = (a,b,c,d,e,a)
		cursor.execute(add_info, data_info)
		cnx.commit()
		cursor.close()
		cnx.close()

	def deletdata(self,a):
		cnx = mysql.connector.connect(user='neil', password='neil',
                              host='52.193.112.188',
                              database='python')
		cursor = cnx.cursor()
		tomorrow = datetime.now().date() + timedelta(days=1)
		add_info = ("delete from information where Name ='%s'" %(a,))

		#data_info = a
		cursor.execute(add_info)
		cnx.commit()
		cursor.close()
		cnx.close()

	def querydata(self):
#		x={}
		cnx = mysql.connector.connect(user='neil', password='neil',
                              host='52.193.112.188',
                              database='python')
		cursor = cnx.cursor()
		tomorrow = datetime.now().date() + timedelta(days=1)
		add_info = ("select * from information ")

		#data_info = a
		cursor.execute(add_info)
		results = cursor.fetchall()
		x=[]
		y=0
		for info in results:
			a=info[0]
			b=info[1]
			c=info[2]
			d=info[3]
			e=info[4]
			f=info[5]
			a="ID=%s,Name=%s,Birthday=%s,Identification=%s,Phone=%s,Address=%s" %(a,b,c,d,e,f) 
			x.append(a)
		cnx.commit()
		cursor.close()
		cnx.close()


		return "\n".join(x)

		
		

	def insertb(self):
		self.insertdata(self.named.get(),self.birthd.get(),self.idd.get(),self.phoned.get(),self.addrd.get())
		self.message["text"]="Susseced "
		
	def updateb(self):
		self.updatedata(self.named.get(),self.birthd.get(),self.idd.get(),self.phoned.get(),self.addrd.get())
		self.message["text"]="Susseced "

	def deleteb(self):
		self.deletdata(self.named.get())
		self.message["text"]="Susseced "

	def queryb(self):
		self.message["text"]=self.querydata()


if __name__ == "__main__":
	root = Tk()
	app = InfoGUI(master=root)
	app.mainloop()