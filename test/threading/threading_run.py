import  threading, time, random    
count =  0    
class  Counter(threading.Thread):    
    def  __init__( self , lock, threadName):    
           
        super(Counter,  self ).__init__(name = threadName)  
        self.lock = lock    
        
    def  run( self ):    
        global  count    
        print self.name
        self.lock.acquire()    
        for  i  in  range(1000):    
            count = count +  1    
        self .lock.release()    
lock = threading.Lock()    
for  i  in  range(5):     
    Counter(lock,  "thread-"  + str(i)).start()   
time.sleep( 2 )        
print("Count={0}!".format(count))   
