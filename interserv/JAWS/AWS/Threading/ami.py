#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import urllib2
import datetime
import json
import os.path
import time
from boto3 import Session
from threading import Thread
import botoapi
imageids={}
class create_image(Thread):
	def __init__(self,regionid,instanceid,imagename):
		global imageids
		Thread.__init__(self)
		self.regionid=regionid
		self.instanceid=instanceid
		self.imagename=imagename
		self.imageid=None
		imageids={}
	def run(self):
		global imageids
		session=Session(region_name=self.regionid)
		ec2=session.client("ec2")
		imageid=botoapi.safecall(
			ec2.create_image,
			InstanceId=self.instanceid,
			Name=self.imagename,
			Description='Create from instanceid '+self.instanceid,
			NoReboot=True)["ImageId"]
		#print self.imageid
		#Do not use ec2.get_waiter, it will throw error if image not avaiiable for 10 mintues
		while True:
			time.sleep(5)
			imageinfo=botoapi.safecall(ec2.describe_images,
				ImageIds=[imageid])["Images"][0]["State"]
			if imageinfo=="available":
				imageids[self.imagename]=imageid
				print "Instance Image for "+self.imagename+" Created"
				self.imageid=imageid
				break
			elif imageinfo=="pending":
				print "Waiting for Creating Image: " +self.imagename
				pass
			else:
				print "Something Wrong on Create Instance Image for "+self.self.imagename
				imageids[self.imagename]="Error"
				self.imageid=None
				break
	def __del__(self):
		pass

class delete_image(Thread):
	def __init__(self,regionid,imageid):
		Thread.__init__(self)
		self.regionid=regionid
		self.imageid=imageid
	def run(self):
		ec2=Session(region_name=self.regionid).client("ec2")
		botoapi.safecall(
			ec2.deregister_image,
			ImageId=self.imageid)
		while True:
			time.sleep(5)
			imageinfo=botoapi.safecall(
				ec2.describe_images,
				ImageIds=[self.imageid])["Images"]
			if len(imageinfo)==0:
				print "Instance Image for "+self.imageid+" Deleted"
				break
			elif imageinfo[0]["State"]=="deregistered":
				print "Instance Image for "+self.imageid+" Deleted"
				break
	def __del__(self):
		pass
class get_image_device_maps(Thread):
	def __init__(self,regionid,imageid):
		Thread.__init__(self)
		self.regionid=regionid
		self.imageid=imageid
		self.device_maps=None
	def run(self):
		ec2=Session(region_name=self.regionid).client("ec2")
		self.device_maps=botoapi.safecall(
			ec2.describe_images,
			ImageIds=[self.imageid])["Images"][0]["BlockDeviceMappings"]
