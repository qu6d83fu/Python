from threading import *
import time

class itemX:
    def __init__(self):
        self.cnt = 0

    def produce (self,num=1):
        self.cnt += 1

    def consume(self,num=1):
        if self.cnt:
            self.cnt -= 1
        else:
            print 'WARNING******WARNING'

    def isEmpty(self):
        return not self.cnt

    def getCount(self):
        return self.cnt

class Producer(Thread):
    def __init__(self, condition, item, sleeptime=2):
        Thread.__init__(self)
        self.con=condition
        self.item=item
        self.sleeptime=sleeptime

    def run(self):
        while(True):
            time.sleep(self.sleeptime)
            self.con.acquire()
            self.item.produce()
            print 'produce 1 product\r\n'
            print self.item.getCount()
            self.con.notifyAll()
            self.con.release()

class Consumer(Thread):
    def __init__(self, condition, item, sleeptime=2):
        Thread.__init__(self)
        self.con=condition
        self.item=item
        self.sleeptime=sleeptime
    def run(self):
        while(True):
            time.sleep(self.sleeptime)
            self.con.acquire()
            print '({0})enter'.format(self.getName())
            while self.item.isEmpty():
                print '({0})wait'.format(self.getName())
                self.con.wait()
            self.item.consume()
            print '({0})consume 1 product\r\n'.format(self.getName())
            print self.item.getCount()
            self.con.release()

if __name__=="__main__":
    X=itemX()
    cond = Condition()
    Producer(cond,X).start()
    Consumer(cond,X).start()
    Consumer(cond,X).start()
    
    while (True):
        pass
    
