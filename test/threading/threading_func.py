import  threading, time, random    
count =  0    
lock = threading.Lock()    
def  doAdd():    
    global  count, lock    
    lock.acquire()    
    for  i  in  range( 1000 ):    
        count = count +  1    
        
    lock.release()  
      
for  i  in  range( 200):    
    threading.Thread(target = doAdd, args = (), name =  'thread-'  + str(i)).start()    
    print 'thread-'  + str(i)
time.sleep( 2 )    
print("Count={0}!".format(count))
