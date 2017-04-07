# -*- coding: UTF-8 -*-
#---- Condition      
import  threading, time    
class  Hider(threading.Thread):    
    def  __init__( self , cond, name):    
        super(Hider,  self ).__init__()    
        self.cond = cond    
        self.name = name    
        
    def  run( self ):    
        time.sleep( 1 )  
            
        self.cond.acquire()  #b        
        print('To {0}: 我已經把眼睛蒙上了'.format(self.name))  
        print("\t[Info] {0} notify()...".format(self.name))  
        self.cond.notify()  
        print("\t[Info] {0} wait()...".format(self.name))  
        self.cond.wait()  #c        
                         #f     
        print('To {0}: 我找到你了~_~'.format(self.name))  
        print("\t[Info] {0} notify()...".format(self.name))  
        self.cond.notify()  
        print("\t[Info] {0} release()...".format(self.name))  
        self.cond.release()    
                            #g    
        print('To {0}: 我贏了'.format(self.name))    #h    
            
class  Seeker(threading.Thread):    
    def  __init__( self , cond, name):    
        super(Seeker,  self ).__init__()    
        self.cond = cond    
        self.name = name    
    def  run( self ):    
        self.cond.acquire()  
        print("\t[Info] {0} wait()...".format(self.name))  
        self.cond.wait()     #a    
                            #d    
        print('To {0}: 我已經藏好了，你快來找我吧'.format(self.name))  
        print("\t[Info] {0} notify()...".format(self.name))  
        self.cond.notify()  
        print("\t[Info] {0} wait()...".format(self.name))  
        self.cond.wait()     #e    
                            #h  
        print("\t[Info] {0} release()...".format(self.name))  
        self.cond.release()     
        print('To {0}: 被你找到了，哎~~~'.format(self.name) )   
            
cond = threading.Condition()    
seeker = Seeker(cond,  'seeker' )    
hider = Hider(cond,  'hider' )    
seeker.start()    
#hider.start()  
