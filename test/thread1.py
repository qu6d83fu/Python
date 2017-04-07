import Queue
import time
import datetime
import threading 
class Job:
	def __init__(self,name):
		self.name=name

	def do(self):
		time.sleep(2)
		print"\t[Info] Job({0}) is done!".format(self.name)


que=Queue.Queue()
for i in range(20):
	que.put(Job(str(i+1)))

print "\t[Info] Queue size={0}".format(que.qsize())

#Single thread
#st=datetime.datetime.now()

#while que.qsize() > 0:
#	job=que.get()
#	job.do()
#	print que.qsize()

#td=datetime.datetime.now() - st

#print "\t[Info] spending time={0}!".format(td)

#Multi thread
def doJob(*args):
	queue=args[0]
	while queue.qsize() > 0:
		job = queue.get()
		job.do()

#Open three threads
thd1=threading.Thread(target=doJob, name='Thd1', args=(que,))
thd2=threading.Thread(target=doJob, name='Thd2', args=(que,))
thd3=threading.Thread(target=doJob, name='Thd3', args=(que,))
thd4=threading.Thread(target=doJob, name='Thd4', args=(que,))
thd5=threading.Thread(target=doJob, name='Thd5', args=(que,))
thd6=threading.Thread(target=doJob, name='Thd6', args=(que,))
thd7=threading.Thread(target=doJob, name='Thd7', args=(que,))

st = datetime.datetime.now()
thd1.start()
thd2.start()
thd3.start()
thd4.start()
thd5.start()
thd6.start()
thd7.start()


#Wait for all threads to terminate.

while thd1.is_alive() or thd2.is_alive() or thd3.is_alive():
	time.sleep(1)

td=datetime.datetime.now() - st
print "\t[Info] Spending time{0}!".format(td)
print datetime.datetime.now()