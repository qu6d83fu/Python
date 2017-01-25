#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf8")
from Threading import instance
from Threading import ami
import boto3
import re
from Threading import botoapi
def get_instanceids(region_id=None,InstanceNames=None):
	#InstanceNames format [<instancename>,<instancename>.....]
	threads=[]
	for i in InstanceNames:
		t=instance.get_instanceid(region_id,i)
		t.start()
		threads.append(t)
	for i in threads:
		i.join()
	# return format [{<InstanceName>:<InatanceId>},{<InstnceName>:None},.....] if None exists means error(Duplicated or NotFound)
	return instance.instanceids

def get_instancenames(region_id=None,InstanceIds=None):
	#InstanceIds format [<instanceid>,<instanceid>.....]
	threads=[]
	for i in InstanceIds:
		t=instance.get_instancename(region_id,i)
		t.start()
		threads.append(t)
	for i in threads:
		i.join()
	# return format [{<InatanceId>:<InstanceName>},{<InstnceId>:None},.....] if None exists means error(NotFound)
	return instance.instancenames



def create_images(region_id=None,InstanceIds_ImageNames=None):
	#InstanceIds_AmiNames format {<InstanceId>:<imagename>,<InstanceId>:<imagename>,....}
	threads=[]
	for i in InstanceIds_ImageNames:
		t=ami.create_image(region_id,i,InstanceIds_ImageNames[i])
		t.start()
		threads.append(t)
	for i in threads:
		i.join()
	# return format [{<ImageName>:<ImageId>},{<ImageName>:None},....] if None exists means unknow error
	return ami.imageids

def delete_images(region_id=None,ImageIds=None):
	#ImageIds format [<imageid>,<imageid>.....]
	threads=[]
	for i in ImageIds:
		t=ami.delete_image(region_id,i)
		t.start()
		threads.append(t)
	for i in threads:
		i.join()

def fuzzy_search_instances(region_id=None,SearchKey=None):
	# seachkey support regular expression
	instances=[]
	ec2=boto3.Session(region_name=region_id).client("ec2")
	nexttoken=""
	while nexttoken is not None:
		if nexttoken=="":
			ec2info=botoapi.safecall(ec2.describe_instances,MaxResults=20)
		else:
			ec2info=botoapi.safecall(ec2.describe_instances,MaxResults=20,NextToken=nexttoken)
		try:
			nexttoken=ec2info["NextToken"]
		except:
			nexttoken=None
		ec2info=ec2info["Reservations"]
		for e in ec2info:
			for i in e["Instances"]:
				if i["State"]["Name"]=="running":
					for t in i["Tags"]:
						if t["Key"]=="Name":
							if re.search(SearchKey,t["Value"]):
								instances.append(t["Value"])
	return sorted(instances)

def fuzzy_search_auto_scaling_groups(region_id=None,SearchKey=None):
	autoscalings=[]
	asg=boto3.Session(region_name=region_id).client("autoscaling")
	nexttoken=""
	while nexttoken is not None:
		if nexttoken=="":
			asgs=botoapi.safecall(asg.describe_auto_scaling_groups,MaxRecords=20)
		else:
			asgs=botoapi.safecall(asg.describe_auto_scaling_groups,MaxRecords=20,NextToken=nexttoken)
		try:
			nexttoken=asgs["NextToken"]
		except:
			nexttoken=None
		asgs=asgs["AutoScalingGroups"]	
		for a in asgs:
			if re.search(SearchKey,a["AutoScalingGroupName"]):
				autoscalings.append(a["AutoScalingGroupName"])
	return autoscalings	

