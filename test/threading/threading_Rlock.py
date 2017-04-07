import  threading    
rLock = threading.RLock()
rLock.acquire()    
rLock.acquire()
rLock.release()    
rLock.release()
