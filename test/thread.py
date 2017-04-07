from threading import *
import Queue
import time

class MyThread(Thread):
	def __init__(self,condition):
		Thread.__init__(self)
		self.cond=condition

	def run(self):
		print '{0} start\r\n'.format(self.getName())
		global cnt
		while (True):
			id = threadPool.get()
			if id != None:
				self.cond.acquire()
			print '{0}_{1}'.format(self.getName(), id)
			for x in xrange(1):
				cnt += x
				time.sleep(2)
			print 'cnt = {0}\r\n'.format(cnt)
			cnt=0
			self.cond.release()
			threadPool.task_done()

threadPool= Queue.Queue(0)
condition = Condition()
cnt=0
for i in xrange(10):
	MyThread(condition).start()

for i in xrange(10):
	threadPool.put(i)

threadPool.join()
print 'done'