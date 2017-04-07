#!/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf8")
from AWS.Threading import instance
from AWS.Threading import ami
from AWS.Threading import autoscaling
from AWS.Threading import elb
from threading import Thread
from AWS import ec2
import datetime
import json
import os.path
from AWS.Threading import botoapi

class rebootinstance(Thread):
        def __init__(self,regionid,serverinfo):
                Thread.__init__(self)
                self.regionid=regionid
                self.instanceid=serverinfo["InstanceID"]
                self.instanceip=serverinfo["InstanceIP"]
        def run(self):
                t=instance.reboot_instance(self.regionid,self.instanceid,self.instanceip)
                t.start()
                t.join()

class startmaintainserver(Thread):
	def __init__(self,regionid,serverinfo):
		Thread.__init__(self)
		self.regionid=regionid
		self.instanceid=serverinfo["InstanceID"]
		self.demeangroup=serverinfo["AutoScalingGroups"]["OnDemean"]
		self.spotgroup=serverinfo["AutoScalingGroups"]["Spot"]
	def run(self):
		# launch instance and wait inservice 
		t=autoscaling.change_auto_scaling_group_size(self.regionid,self.demeangroup,1,1)
		t.start()
		t.join()
		launchedinstanceids=t.instanceids
		# get elb from autoscaling group
		t=autoscaling.get_auto_scaling_group(self.regionid,self.demeangroup)
		t.start()
		t.join()
		elbs=t.elbs
		threads=[]
		for e in elbs:
			for i in launchedinstanceids:
				t=elb.check_instance_inservice(self.regionid,e,i)
				t.start()
				threads.append(t)
		for t in threads:
			t.join()
		#remove seed instance from elbs
		threads=[]
		for e in elbs:
			t=elb.remove_instance_from_elb(self.regionid,e,self.instanceid)
			t.start()
			threads.append(t)
		for t in threads:
			t.join()
		print "Server "+ self.instanceid+ " ready to maintain"

def startmaintain(filename):
	product=json.load(open(filename,"r"))
	regionid=product["RegionID"]
	#gather all inatanceid
	autoscalings=[]
	for s in product["Servers"]:
		autoscalings.append(s["AutoScalingGroups"]["OnDemean"])
		if s["AutoScalingGroups"]["Spot"]!= "":
			autoscalings.append(s["AutoScalingGroups"]["Spot"])
	threads=[]
	for a in autoscalings:
		t=autoscaling.check_auto_scaling_group_exists(regionid,a)
		t.start()
		threads.append(t)
	for t in threads:
		t.join()
	exists=True
	for t in threads:
		if t.exists==False:
			exists=False
			break
	if not exists:
		print "Some AutoScalingGroup does not exist, mission abort!!!"
	else:
		instanceids=[]
		for s in product["Servers"]:
			instanceids.append(s["InstanceID"])
		instances=botoapi.safecall(ec2.get_instancenames,region_id=regionid,InstanceIds=instanceids)
		names=sorted(instances.values())
		for a in names:
			print a
		start=raw_input("Above servers will start maintain, contuine? (Y/n) ")
		if start=="Y":
			threads=[]
			for s in product["Servers"]:
				t=startmaintainserver(regionid,s)
				t.start()
				threads.append(t)
			for t in threads:
				t.join()

class maintainautoscaling(Thread):
	def __init__(self,regionid,scalingname,imageid):
		Thread.__init__(self)
		self.regionid=regionid
		self.scalingname=scalingname
		self.imageid=imageid
	def run(self):
		newname=self.scalingname.split("-")
		newname.pop()
		newname=newname+[unicode(datetime.datetime.now().strftime("%Y%m%d%H%M"),"utf-8")]
		newname=u"-".join(newname)
		asg=autoscaling.get_auto_scaling_group(self.regionid,self.scalingname)
		asg.start()
		asg.join()
		self.elbs=asg.elbs
		oldconfig=asg.launchconfig
		asg=autoscaling.copy_launchconfig(self.regionid,oldconfig,newname,self.imageid)
		asg.start()
		asg.join()
		self.oldimageid=asg.oldimageid
		asg=autoscaling.set_auto_scaling_group_launchconfig(self.regionid,self.scalingname,newname)
		asg.start()
		asg.join()
		asg=autoscaling.set_auto_scaling_group_instance_name(self.regionid,self.scalingname,newname)
		asg.start()
		asg.join()
		asg=autoscaling.delete_launchconfig(self.regionid,oldconfig)
		asg.start()
		asg.join()
		print "AutoScaling "+ self.scalingname+ " Completed"








class finishmaintainserver(Thread):
	def __init__(self,regionid,serverinfo):
		Thread.__init__(self)
		self.regionid=regionid
		self.instanceid=serverinfo["InstanceID"]
		self.demeangroup=serverinfo["AutoScalingGroups"]["OnDemean"]
		self.spotgroup=serverinfo["AutoScalingGroups"]["Spot"]
	def run(self):
		t=instance.get_instancename(self.regionid,self.instanceid)
		t.start()
		t.join()
		instancename=t.instancename
		imagename=instancename.split("-")
		imagename.pop()
		imagename=imagename+[unicode(datetime.datetime.now().strftime("%Y%m%d%H%M"),"utf-8")]
		imagename=u"-".join(imagename)
		t=ami.create_image(self.regionid,self.instanceid,imagename)
		t.start()
		t.join()
		threads=[]
		newimageid=t.imageid
		t=maintainautoscaling(self.regionid,self.demeangroup,newimageid)
		t.start()
		threads.append(t)
		if self.spotgroup != "":
			t=maintainautoscaling(self.regionid,self.spotgroup,newimageid)
			t.start()
			threads.append(t)
		for t in threads:
			t.join()
		elbs=t.elbs
		oldimageid=t.oldimageid
		threads=[]
		for e in elbs:
			t=elb.add_instance_to_elb(self.regionid,e,self.instanceid)
			t.start()
			threads.append(t)
		for t in threads:
			t.join()
		t=instance.set_instance_name(self.regionid,self.instanceid,imagename)
		t.start()
		t.join()
		t=ami.delete_image(self.regionid,oldimageid)
		t.start()
		t.join()
		t=autoscaling.change_auto_scaling_group_size(self.regionid,self.demeangroup,0,0)
		t.start()
		t.join()
		print "Finish "+ imagename +" Maintainance."

def finishmaintain(filename):
	product=json.load(open(filename,"r"))
	regionid=product["RegionID"]
	#gather all autoscaling
	autoscalings=[]
	for s in product["Servers"]:
		autoscalings.append(s["AutoScalingGroups"]["OnDemean"])
		if s["AutoScalingGroups"]["Spot"]!= "":
			autoscalings.append(s["AutoScalingGroups"]["Spot"])
	threads=[]
	for a in autoscalings:
		t=autoscaling.check_auto_scaling_group_exists(regionid,a)
		t.start()
		threads.append(t)
	for t in threads:
		t.join()
	exists=True
	for t in threads:
		if t.exists==False:
			exists=False
			break
	if not exists:
		print "Some AutoScalingGroup does not exist, mission abort!!!"
	else:
		start=raw_input("All AutoScalingGroup exists ready to finish maintain, contuine? (Y/n) ")
		if start=="Y":
			threads=[]
			regionid=product["RegionID"]
			for s in product["Servers"]:
				t=finishmaintainserver(regionid,s)
				t.start()
				threads.append(t)
			for t in threads:
				t.join()
def rebootserver(filename):
	product=json.load(open(filename,"r"))
        regionid=product["RegionID"]
	instanceids=[]
        for s in product["Servers"]:
        	instanceids.append(s["InstanceID"])
        instances=botoapi.safecall(ec2.get_instancenames,region_id=regionid,InstanceIds=instanceids)
        names=sorted(instances.values())
        for a in names:
        	print a
        start=raw_input("Above servers will reboot, contuine? (Y/n) ")
        if start=="Y":
        	threads=[]
                for s in product["Servers"]:
                	t=rebootinstance(regionid,s)
                        t.start()
                        threads.append(t)
                for t in threads:
                	t.join()
                        
			

if __name__=="__main__":
	if len(sys.argv)==3:
		filename=sys.argv[1]
		action=sys.argv[2]
		if not os.path.exists(filename):
			print filename+ " does not exists"
		elif action !="start" and action !="finish" and action !="reboot":
			print "syntax: python maintain.py <path-to-Server-Structure-file> <start|finish>"
                        sys.exit()
		if action=="start":
			startmaintain(filename)
		elif action=="reboot":
			rebootserver(filename)
		else:
			finishmaintain(filename)
	else:
		print "syntax: python maintain.py <path-to-Server-Structure-file> <start|finish>"
#startmaintain("id.json")
