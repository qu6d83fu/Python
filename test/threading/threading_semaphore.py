# coding=UTF-8  
import threading, time, random   
  
count=0  
round=3
lock=threading.Lock()  
sem=threading.Semaphore(5)  # Code block can be executed by at most 5 threads concurrently  
def codeBlock(thd, i):  
    global count  
    lock.acquire()  
    count+=1  
    print "\t[Info] {0}/{1} entering({2})...".format(thd.name, i, count)      
    lock.release()      
    time.sleep(random.randrange(2,10))  
    lock.acquire()  
    count-=1  
    print "\t[Info] {0}/{1} exit({2})...".format(thd.name, i, count)      
    lock.release()  
      
class Guest(threading.Thread):  
    def  __init__( self , lock, threadName):  
        super(Guest,  self ).__init__(name = threadName)   #注意：一定要顯式的調用父類的初始化函數.    
        self.lock = lock  
          
    def  run( self ):      
        '''@summary:重寫父類run方法，在線程啟動後執行該方法內的代碼. '''      
        global  count                  
        for  i  in  range(round):  
            self.lock.acquire()      
            codeBlock(self, i)      
            self.lock.release()  
        print "\t[Info] {0} Bye!".format(self.name)  
          
for  i  in  range(4):       
    Guest(sem,  "thread-"+ str(i)).start()   # Open 10 隻線程
