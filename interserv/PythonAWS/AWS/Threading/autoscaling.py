#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf8")
from threading import Thread
import boto3
import re
import time
import ami
import botoapi
class check_auto_scaling_group_exists(Thread):
	def __init__(self,regionid,groupname):	
		Thread.__init__(self)
		self.regionid=regionid
		self.groupname=groupname
		self.groupinfo={}
		self.exists=False
	def run(self):
		asg=boto3.Session(region_name=self.regionid).client("autoscaling")
		if len(botoapi.safecall(asg.describe_auto_scaling_groups,AutoScalingGroupNames=[self.groupname])["AutoScalingGroups"])==0:
			self.exists=False
		else:
			self.exists=True

class get_auto_scaling_group(Thread):
	def __init__(self,regionid,groupname):	
		Thread.__init__(self)
		self.regionid=regionid
		self.groupname=groupname
		self.groupinfo={}
	def run(self):
		asg=boto3.Session(region_name=self.regionid).client("autoscaling")
		self.groupinfo=botoapi.safecall(asg.describe_auto_scaling_groups,AutoScalingGroupNames=[self.groupname])["AutoScalingGroups"][0]
		#self.groupinfo refers to https://boto3.readthedocs.io/en/latest/reference/services/autoscaling.html#AutoScaling.Client.describe_auto_scaling_groups
		self.launchconfig=self.groupinfo["LaunchConfigurationName"]
		self.elbs=self.groupinfo["LoadBalancerNames"]
		self.desired=self.groupinfo["DesiredCapacity"]

class change_auto_scaling_group_size(Thread):
	def __init__(self,regionid,groupname,min,desired):
		Thread.__init__(self)
		self.regionid=regionid
		self.groupname=groupname
		self.min=min
		self.desired=desired
		self.groupinfo=None
		self.instanceids=[]
	def run(self):
		asg=boto3.Session(region_name=self.regionid).client("autoscaling")
		botoapi.safecall(asg.update_auto_scaling_group,AutoScalingGroupName=self.groupname,MinSize=self.min, DesiredCapacity=self.desired)
		while True:
			asgstatus=get_auto_scaling_group(self.regionid,self.groupname)
			asgstatus.start()
			asgstatus.join()
			ready=False

			if len(asgstatus.groupinfo["Instances"])==self.desired:
				ready=True
				self.instanceids=[]
				for i in asgstatus.groupinfo["Instances"]:
					#print i["LifecycleState"]
					self.instanceids.append(i["InstanceId"])
					if i["LifecycleState"] != "InService":
						ready=False
						break
			if ready:
				break
			time.sleep(5)
		print self.groupname+" Changed"
		self.groupinfo=asgstatus.groupinfo

class set_auto_scaling_group_launchconfig(Thread):
	def __init__(self,regionid,autoscalingname,launchconfigname):
		Thread.__init__(self)
		self.regionid=regionid
		self.autoscalingname=autoscalingname
		self.launchconfigname=launchconfigname
	def run(self):
		asg=boto3.Session(region_name=self.regionid).client("autoscaling")
		botoapi.safecall(
			asg.update_auto_scaling_group,
			AutoScalingGroupName=self.autoscalingname,
			LaunchConfigurationName=self.launchconfigname)



class set_auto_scaling_group_instance_name(Thread):
	def __init__(self,regionid,autoscalingname,instancename):
		Thread.__init__(self)
		self.regionid=regionid
		self.instancename=instancename
		self.autoscalingname=autoscalingname
	def run(self):
		asg=boto3.Session(region_name=self.regionid).client("autoscaling")
		botoapi.safecall(
			asg.create_or_update_tags,
			Tags=[{"ResourceId":self.autoscalingname,
			"ResourceType":"auto-scaling-group",
			"Key":"Name",
			"Value":self.instancename,
			"PropagateAtLaunch":True
			}])

class copy_launchconfig(Thread):
	def __init__(self,regionid,srcname,destname,destimageid):
		Thread.__init__(self)
		self.regionid=regionid
		self.srcname=srcname
		self.destname=destname
		self.destimageid=destimageid
		self.oldimageid=None
	def run(self):
		asg=boto3.Session(region_name=self.regionid).client("autoscaling")
		launchInfo=botoapi.safecall(
			asg.describe_launch_configurations,
			LaunchConfigurationNames=[self.srcname])["LaunchConfigurations"][0]
		self.oldimageid=launchInfo["ImageId"]
		imageID=self.destimageid
		keyName=launchInfo["KeyName"]
		securityGroups=launchInfo["SecurityGroups"]
		userData=launchInfo["UserData"]
		instanceType=launchInfo["InstanceType"]
		kernelID=launchInfo["KernelId"]
		ramDiskID=launchInfo["RamdiskId"]
		t=ami.get_image_device_maps(self.regionid,self.destimageid)
		t.start()
		t.join()
		blockDeviceMappings=t.device_maps
		#Parameter encrypted is invalid. You cannot specify the encrypted flag if specifying a snapshot id in a block device mapping.
		#Remove encrypted flag
		#Root Device don't need the snapshotid, so remove it also
		for d in blockDeviceMappings:
			if d["DeviceName"]=="/dev/sda1":
				d["Ebs"].pop("SnapshotId")
			d["Ebs"].pop("Encrypted")
			
		instanceMonitoring=launchInfo["InstanceMonitoring"]
		try:
			spotPrice=launchInfo["SpotPrice"]
		except:
			spotPrice=None
		ebsOptimized=launchInfo["EbsOptimized"]
		if spotPrice is not None:
			botoapi.safecall(
				asg.create_launch_configuration,
				LaunchConfigurationName=self.destname,
				ImageId=imageID,
				KeyName=keyName,
				UserData=userData,
				SecurityGroups=securityGroups,
				InstanceType=instanceType,
				BlockDeviceMappings=blockDeviceMappings,
				InstanceMonitoring=instanceMonitoring,
				SpotPrice=spotPrice,
				EbsOptimized=ebsOptimized)
		else:
			botoapi.safecall(
				asg.create_launch_configuration,
				LaunchConfigurationName=self.destname,
				ImageId=imageID,
				KeyName=keyName,
				UserData=userData,
				SecurityGroups=securityGroups,
				InstanceType=instanceType,
				BlockDeviceMappings=blockDeviceMappings,
				InstanceMonitoring=instanceMonitoring,
				EbsOptimized=ebsOptimized)

class delete_launchconfig(Thread):
	def __init__(self,regionid,launchconfigname):
		Thread.__init__(self)
		self.regionid=regionid
		self.launchconfigname=launchconfigname
	def run(self):
		asg=boto3.Session(region_name=self.regionid).client("autoscaling")
		botoapi.safecall(
			asg.delete_launch_configuration,
			LaunchConfigurationName=self.launchconfigname)

