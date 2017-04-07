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
class check_instance_inservice(Thread):
	def __init__(self,regionid,elbname,instanceid):
		Thread.__init__(self)
		self.regionid=regionid
		self.elbname=elbname
		self.instanceid=instanceid
	def run(self):
		elb=Session(region_name=self.regionid).client("elb")
		inservice=False
		while not inservice:
			instancestate=botoapi.safecall(
				elb.describe_instance_health,
				LoadBalancerName=self.elbname,
				Instances=[{"InstanceId":self.instanceid}])
			if len(instancestate["InstanceStates"])==1:
				if instancestate["InstanceStates"][0]["State"]=="InService":
					inservice=True
				else:
					print "Instance "+self.instanceid+" "+instancestate["InstanceStates"][0]["State"]
					time.sleep(5)
			else:
				print "Instance "+self.instanceid+" not yet present"
				time.sleep(5)
		print "Instance " + self.instanceid+" in "+self.elbname+" InService" 
				

class add_instance_to_elb(Thread):
	def __init__(self,regionid,elbname,instanceid):
		Thread.__init__(self)
		self.regionid=regionid
		self.elbname=elbname
		self.instanceid=instanceid
	def run(self):
		elb=Session(region_name=self.regionid).client("elb")
		botoapi.safecall(
			elb.register_instances_with_load_balancer,
			LoadBalancerName=self.elbname,
			Instances=[{"InstanceId":self.instanceid}]
			)
		a=check_instance_inservice(self.regionid,self.elbname,self.instanceid)
		a.start()
		a.join()
class check_instance_removed(Thread):
	def __init__(self,regionid,elbname,instanceid):
		Thread.__init__(self)
		self.regionid=regionid
		self.elbname=elbname
		self.instanceid=instanceid
	def run(self):
		elb=Session(region_name=self.regionid).client("elb")
		removed=False
		while not removed:
			instancestate=botoapi.safecall(
				elb.describe_instance_health,
				LoadBalancerName=self.elbname,
				Instances=[{"InstanceId":self.instanceid}])
			if len(instancestate["InstanceStates"])==1:
				if instancestate["InstanceStates"][0]["State"]=="OutOfService":
					removed=True
				else:
					time.sleep(5)
					print "Waiting for instance remove from ELB "+self.elbname
			else:
				time.sleep(5)
				print "Waiting for instance remove from ELB "+self.elbname


class remove_instance_from_elb(Thread):
	def __init__(self,regionid,elbname,instanceid):
		Thread.__init__(self)
		self.regionid=regionid
		self.elbname=elbname
		self.instanceid=instanceid
	def run(self):
		elb=Session(region_name=self.regionid).client("elb")
		botoapi.safecall(
			elb.deregister_instances_from_load_balancer,
			LoadBalancerName=self.elbname,
			Instances=[{"InstanceId":self.instanceid}]
			)
		a=check_instance_removed(self.regionid,self.elbname,self.instanceid)
		a.start()
		a.join()
		print "Instance " + self.instanceid+" removed from ELB "+self.elbname

class check_elb_inservice(Thread):
	def __init__(self,regionid,elbname):
		Thread.__init__(self)
		self.regionid=regionid
		self.elbname=elbname
	def run(self):
		elb=Session(region_name=self.regionid).client("elb")
		inservice=False
		print "Waiting for instances under ELB "+self.elbname+ " InService"
		while not inservice:
			inservice=True
			instancestate=botoapi.safecall(
				elb.describe_instance_health,
				LoadBalancerName=self.elbname)
			for i in instancestate["InstanceStates"]:
				#print i["State"]
				if i["State"]=="OutOfService":
					inservice=False
			if not inservice:
				time.sleep(5)
		print "All instances under ELB "+self.elbname+ " InService"
