#coding=utf-8
import os.path
import datetime
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import json
from threading import Thread
import AWS.autoscaling
import AWS.ec2
import AWS.elb
#import threading
class startflow(Thread):
    def __init__(self,region,server):
        Thread.__init__(self)
        self.region=region
        self.instanceid=server['InstanceID']
        self.groupname=server['AutoScalingGroup']
    def run(self):
#Extening auto scaling group
        t=AWS.autoscaling.change_auto_scaling_group_size(self.region,self.groupname,1,1)
        t.start()
        t.join()
        elbs=t.elbs
        launchedinstanceids=t.instanceids
#Checking ELB InService
        thread=[]
        for e in elbs:
            for i in launchedinstanceids:
                t=AWS.elb.check_instance_inservice(self.region,e,i)
                t.start()
                thread.append(t)
            for t in thread:
                t.join()
#Removing seed instance
        thread=[]
        for e in elbs:
            t=AWS.elb.deregister_instance_from_elb(self.region,e,self.instanceid)
            t.start()
            thread.append(t)
        for t in thread:
            t.join()

def start():
#setting default parameters
    product=json.load(open(filename,'r'))
    region=product['Region']
    servers=product['ServerInfo']
#Checking the autoscaling groups exist,if not exist that will exit the program.
    thread=[]
    fail=[]
    for a in servers:
        groupname=a['AutoScalingGroup']
        t=AWS.autoscaling.check_auto_scaling_group_exist(region,groupname)
        t.start()
        thread.append(t)
    for t in thread:
        t.join()
    for t in thread:
        exit=False
        exist=t.exist
        if not exist :
            exit=True            
    if exit:
        for a in AWS.autoscaling.failgroupnames:
            print a + ' not exist'
        sys.exit()            
#Showing instancename that you have configured.
    thread=[]
    for a in servers:
        t=AWS.ec2.get_instance_names(region,a['InstanceID'])
        t.start()
        thread.append(t)
    for t in thread:
        t.join()
    for t in thread:
        print t.instancename
#Selecting Y or N to start maintaining servers.
    while True:
        checkstart=raw_input('About instances start maintaining(Y/n): ')
        if checkstart=='Y' or checkstart=='y':
            break
        elif checkstart=='N' or checkstart=='n':
            sys.exit()
        else:
            print 'Please enter (Y/n): '
#changing the autoscaling groups min size and desired size
    thread=[]
    for a in servers:
        t=startflow(region,a)
        t.start()
        thread.append(t)
    for t in thread:
        t.join

class maintainASGgroup(Thread):
    def __init__(self,region,groupname,newimg,imgname):
        Thread.__init__(self)
        self.region=region
        self.groupname=groupname
        self.newimg=newimg
        self.imgname=imgname
    def run(self):
        t=AWS.autoscaling.copy_launch_configuration(self.region,self.groupname,self.newimg)
        t.start()
        t.join()
        oldlaunchconfig=t.oldlaunchconfig
        newlaunchconfig=t.newlaunchconfig
        oldimg=t.oldimg
        self.oldimg=oldimg
        t=AWS.autoscaling.update_auto_scaling_group(self.region,self.groupname,newlaunchconfig,self.imgname)
        t.start()
        t.join()
        t=AWS.autoscaling.delete_launchconfig(self.region,oldlaunchconfig)
        t.start()
        t.join()

class finishflow(Thread):
    def __init__(self,region,server):
        Thread.__init__(self)
        self.region=region
        self.instanceid=server['InstanceID']
        self.groupname=server['AutoScalingGroup']
    def run(self):
        t=AWS.ec2.get_instance_names(self.region,self.instanceid)
        t.start()
        t.join()
        instancename=t.instancename
        imgname=instancename.split("-")
        imgname.pop()
        imgname=imgname+[unicode(datetime.datetime.now().strftime("%Y%m%d%H%M"),"utf-8")]
        imgname=u"-".join(imgname)
        t=AWS.ec2.create_images(self.region,self.instanceid,imgname)
        t.start()
        t.join()
        newimg=t.imgid
#        newimg='ami-b6d883d1'
        t=maintainASGgroup(self.region,self.groupname,newimg,imgname)
        t.start()
        t.join()
        oldimg=t.oldimg
        t=AWS.autoscaling.get_auto_scaling_groups(self.region,self.groupname)
        t.start()
        t.join()
        elbs=t.elbs
        thread=[]
        for e in elbs:
            t=AWS.elb.add_instance_to_elb(self.region,self.instanceid,e)
            t.start()
            thread.append(t)
        for t in thread:
            t.join()
        t=AWS.autoscaling.change_auto_scaling_group_size(self.region,self.groupname,0,0)
        t.start()
        t.join()
        t=AWS.ec2.deregister_images(self.region,oldimg)
        t.start()
        t.join()

def finish():
#Setting default parameters
    product=json.load(open(filename,'r'))
    region=product['Region']
    servers=product['ServerInfo']
#Checking the autoscaling groups exist
    thread=[]
    for a in servers:
        groupname=a['AutoScalingGroup']
        t=AWS.autoscaling.check_auto_scaling_group_exist(region,groupname)
        t.start()
        thread.append(t)
    for t in thread:
        t.join()
    for t in thread:
        exist=t.exist
        if exist != True:
            print groupname + ' Not exist'
            sys.exit()   
    checkfinish=raw_input( 'ASG exists,enter and continue.')
#Finishflow
    thread=[]
    for a in servers:
        t=finishflow(region,a)
        t.start()
        thread.append(t)
    for t in thread:
        t.join()
 
if __name__=='__main__':
    if len(sys.argv)==3:
        #configure file
        filename=sys.argv[1]
        #autoscaling group parameters
        if not os.path.exists(filename):
            print filename + ' not exists'
            sys.exit()
        if sys.argv[2]=='start':
            start()
        elif sys.argv[2]=='finish':
            finish()
        else:
            print 'excute formate "python main.py file.json start|finish"'
    else:
        print 'excute formate "python main.py file.json start|finish"'
