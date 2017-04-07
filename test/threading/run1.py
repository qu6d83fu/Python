import threading
import time

class MyThread(threading.Thread):
    def __init__(self,string,sleeptime):
        threading.Thread.__init__(self)
        self.sleeptime=sleeptime
        self.setName(str(sleeptime))
    def run(self):
        while(True):
            print 'Threadfun_{0}\r\n'.format(self.getName())
            time.sleep(self.sleeptime)

if __name__=="__main__":
    thrList= [MyThread('ThreadFun',i)for i in range(1,5)]

    for i in range(0,4):
        thrList[i].start()
    
