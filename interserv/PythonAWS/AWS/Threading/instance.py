#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import datetime
import json
import os.path
import time
from boto3 import Session
from threading import Thread
import botoapi
import socket
instanceids={}
instancenames={}
class get_instanceid(Thread):
	def __init__(self,regionid,instancename):
		global instanceids
		Thread.__init__(self)
		self.regionid=regionid
		self.instancename=instancename
		self.instanceid=None
		self.instanceinfo=None
		instanceids={}
	def run(self):
		global instanceids
		session=Session(region_name=self.regionid)
		ec2=session.client("ec2")
		instances=botoapi.safecall(ec2.describe_instances,Filters=[{"Name":"tag:Name","Values":[self.instancename]}])["Reservations"]
		if len(instances)>1:
			print "Error: "+ self.instancename+ " Duplicated"
			self.instanceid=None
			instanceids[self.instancename]=self.instancename+ " Duplicated"
		elif len(instances)==0:
			print "Error: "+ self.instancename+ " Not Found"
			self.instanceid=None
			instanceids[self.instancename]=self.instancename+ " Not Found"
		else:
			instanceids[self.instancename]=instances[0]["Instances"][0]["InstanceId"]
			self.instanceinfo=instances[0]["Instances"][0]
			self.instanceid=instances[0]["Instances"][0]["InstanceId"]
	def __del__(self):
		pass

class get_instancename(Thread):
	def __init__(self,regionid,instanceid):
		global instancenames
		Thread.__init__(self)
		self.regionid=regionid
		self.instanceid=instanceid
		self.instancename=None
		instancenames={}

	def run(self):
		global instancenames
		session=Session(region_name=self.regionid)
		ec2=session.client("ec2")
		instances=botoapi.safecall(
			ec2.describe_instances,
			Filters=[{"Name":"instance-id","Values":[self.instanceid]}])["Reservations"]
		if len(instances)==0:
			instancenames[self.instanceid]=self.instanceid+ " Not found"
			self.instancename=None
			print "Error: "+self.instanceid+ " Not found"
		else:
			for tag in instances[0]["Instances"][0]["Tags"]:
				if tag["Key"]=="Name":
					myname=tag["Value"]
					break
			instancenames[self.instanceid]=myname
			self.instanceinfo=instances[0]["Instances"][0]
			self.instancename=myname
	def __del__(self):
		pass
class set_instance_name(Thread):
	def __init__(self,regionid,instanceid,instancename):
		Thread.__init__(self)
		self.regionid=regionid
		self.instanceid=instanceid
		self.instancename=instancename
	def run(self):
		ec2=Session(region_name=self.regionid).client("ec2")
		botoapi.safecall(
			ec2.create_tags,
			Resources=[self.instanceid],
			Tags=[{"Key":"Name","Value":self.instancename}]
			)
class reboot_instance(Thread):
        def __init__(self,regionid,instanceid,instanceip):
                Thread.__init__(self)
                self.regionid=regionid
                self.instanceid=instanceid
                self.instanceip=instanceip
                self.instancename=None
        def run(self):
                ec2=Session(region_name=self.regionid).client("ec2")
                instances=botoapi.safecall(ec2.describe_instances,
                                                InstanceIds=[self.instanceid,]
                                                )["Reservations"]
                for tag in instances[0]["Instances"][0]["Tags"]:
                    if tag["Key"]=="Name":
                        myname=tag["Value"]
                        break
                print myname
                #botoapi.safecall(ec2.reboot_instances,InstanceIds=[self.instanceid,] )
                #time.sleep(10)
                
                #s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                #while True:
                #    try:
                #        s.connect(("IP",22))
                #        print "{0} reboot successful".format(myname)
                #        break
                #    except socket.error :
                #        print "{0}waitting for reboot".format(myname)
                #s.close()

                #while True:
                #    if len(botoapi.safecall(ec2.describe_instance_status,InstanceIds=[self.instanceid],Filters=[{"Name":"instance-status.status","Values":["ok"]}])["InstanceStatuses"])==0:
                #        print "waiting instance reboot"
                #        time.sleep(10)
                #    elif len (botoapi.safecall(ec2.describe_instance_status,InstanceIds=[self.instanceid],Filters=[{"Name":"instance-status.status","Values":["ok"]}])["InstanceStatuses"])==1:
                #        print "reboot successed"
                #        break
                
