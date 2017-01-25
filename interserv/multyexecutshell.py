import threading
import subprocess
import sys

class ExecuteShell(threading.Thread):
	def __init__(self,cmd,date):
		super(ExecuteShell,self).__init__()
		self.cmd=cmd
		self.date=date
	def run(self):
		subprocess.call('{0}'.format(self.cmd),shell=True,cwd='./{0}'.format(self.date))

def main():
	thread=[]
	try:
		date=int(raw_input('Please enter a directory date (ex:20170101): '))
	except ValueError:
		print 'Please enter a date'
		sys.exit()
	file=open('./{0}/dbscript{1}.sh'.format(date,date),'r')
	for cmd in file:
		t=ExecuteShell(cmd,date)
		t.start()
		thread.append(t)
	for t in thread:
		t.join()
		
	file.close()

if __name__=="__main__":
	main()

