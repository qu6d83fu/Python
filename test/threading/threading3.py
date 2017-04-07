import  threading, time    
def  doWaiting():    
    print('\t[Info] start waiting...{0}' , time.strftime( '%H:%M:%S' ))    
    time.sleep( 3 )    
    print('\t[Info] stop waiting...{0}' , time.strftime( '%H:%M:%S' ))    
thread1 = threading.Thread(target = doWaiting)    
thread1.start()    
time.sleep( 1 )
print('start join')    
thread1.join()
print('end join')  
