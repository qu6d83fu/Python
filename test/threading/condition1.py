#---- Condition
import threading, time

class Neil(threading.Thread):
    def __init__(self,cond,name):
        super(Neil,self).__init__()
        self.cond = cond
        self.name = name

    def run(self):
        self.cond.acquire()
        print '{0}:My name is {1}.'.format(self.name,self.name)
        self.cond.wait()
        print '{0}:good to see you guys.'.format(self.name)
        self.cond.release()

class Sandy(threading.Thread):
    def __init__(self,cond,name):
        super(Sandy,self).__init__()
        self.cond = cond
        self.name = name
    
    def run(self):
#        time.sleep(1)
        self.cond.acquire()
        print '{0}:My name is {1},'.format(self.name,self.name)
        self.cond.wait()
        print '{0}:me too'.format(self.name)
        self.cond.notify()
        self.cond.release()

class Winner(threading.Thread):
    def __init__(self,cond,name):
        super(Winner,self).__init__()
        self.cond = cond
        self.name = name

    def run(self):
#        time.sleep(1)
        self.cond.acquire()
        print '{0}:My name is {1},'.format(self.name,self.name)
        self.cond.notify(n=2)
        self.cond.wait()
        print '{0}:glad to see you all'.format(self.name)
        self.cond.release()


cond=threading.Condition()
Neil=Neil(cond,'Neil')
Sandy=Sandy(cond,'Sandy')
Winner=Winner(cond,'Winner')
Neil.start()
Sandy.start()
Winner.start()


        
    
