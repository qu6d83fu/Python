import threading
import subprocess
import shlex
import sys
import os
import re

serverinfo={
	1:"1.SEA_Portal",
	2:"2.NA_Portal",
	3:"3.SEA_Game1",
	4:"4.SEA_Game2",
	5:"5.SEA_Game3",
	6:"6.SEA_Game4",
	7:"7.SEA_Game5",
	8:"8.SEA_Game6",
	9:"9.SEA_Game7",
	10:"10.NA_Game1",
	11:"11.NA_Game2",
	12:"12.NA_Game3"}
		
rdsinfo={
	1:"id-sea-portal.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	2:"id-na-portal.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	3:"id-sea.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	4:"id-sea.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	5:"id-sea.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	6:"id-sea.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	7:"id-sea.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	8:"id-sea.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	9:"id-sea.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	10:"id-na-game01.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	11:"id-na-game01.cugpvv18vihk.us-west-2.rds.amazonaws.com",
	12:"id-na-game01.cugpvv18vihk.us-west-2.rds.amazonaws.com"}
dbinfo={
	1:"id_sea_portal",
	2:"id_sea_portal",
	3:"id_cb_game",
	4:"id_cb2_game",
	5:"id_cb3_game",
	6:"id_cb4_game",
	7:"id_cb5_game",
	8:"id_cb6_game",
	9:"id_cb7_game",
	10:"id_cb_game",
	11:"id_cb2_game",
	12:"id_cb3_game"}

reloadurl={
	1:"",
	2:"",
	3:"http://id-sea-zone8-game01.is520.com:44010",
	4:"http://id-sea-zone8-game02.is520.com:44010",
	5:"http://id-sea-zone8-game03.is520.com:44010",
	6:"http://id-sea-zone8-game04.is520.com:44010",
	7:"http://id-sea-zone8-game05.is520.com:44010",
	8:"http://id-sea-zone8-game06.is520.com:44010",
	9:"http://id-sea-zone8-game07.is520.com:44010",
	10:"http://id-na-zone-6-game01.is520.com:44010",
	11:"http://id-na-zone-6-game01.is520.com:44010",
	12:"http://id-na-zone-6-game01.is520.com:44010"}

servers={}
lock = threading.Lock() 
Rlock = threading.RLock() 

class MultyThreadSQL(threading.Thread):
	def __init__(self,serverinfo,rdsinfo,dbinfo,sqllist,server,num,Rlock):
		super(MultyThreadSQL,self).__init__()
		self.serverinfo=serverinfo
		self.rdsinfo=rdsinfo
		self.dbinfo=dbinfo
		self.sqllist=sqllist
		self.server=server
		self.num=num
		self.Rlock=Rlock
	def run(self):
	#	self.Rlock.acquire()
		print 'RDS_Name = {0} , DomainName = {1} , DB = {2} , SQL = {3}.'.format(self.serverinfo[self.server],self.rdsinfo[self.server],self.dbinfo[self.server],self.sqllist[self.num])
             	sql=open('{0}'.format(self.sqllist[self.num]),'r')
               	subprocess.call(shlex.split('mysql -h{0} -uxy -p6Tfr45 {1}'.format(self.rdsinfo[self.server],self.dbinfo[self.server])),stdin=sql)
	#	self.Rlock.release()
#Show server
for show in serverinfo:
	print serverinfo[show]
print ""
#Chose server
servernum=raw_input('Server number: ')
servernumlist=re.split(',',servernum)
print""
#selected server
print 'Selected Servers:'
for show in servernumlist:
	show=int(show)
	print serverinfo[show]
print ""
	
#show sql file
print 'SQL files'
sqllist=[]
for file in os.listdir("./"):
    if file.endswith(".sql"):
	sqllist.append(file)

for a,b in enumerate(sqllist,1):
		print a,b

sqlnum=raw_input('Enter the sql number,ex:1,2,3,.....: ')

sqlnumlist=re.split(',',sqlnum)
#selected sql file
for num in sqlnumlist:
	num=int(num)-1
	print sqllist[num]
sqlcheck=raw_input('Are you sure importing those sql files (Y/n) :')
threads=[]
lockcount=0
if sqlcheck == 'Y' or sqlcheck == 'y':
	for num in sqlnumlist:
		num=int(num)-1
		for server in servernumlist:
        		server=int(server)
			THR=MultyThreadSQL(serverinfo,rdsinfo,dbinfo,sqllist,server,num,Rlock)
			THR.start()
			
			threads.append(THR)
		for THR in threads:
			THR.join()
else:
	print 'Exit!'
	sys.exit()
