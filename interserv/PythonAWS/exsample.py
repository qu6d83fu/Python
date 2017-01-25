from AWS import ec2
from AWS.Threading import autoscaling
from AWS.Threading import elb
import datetime
def delete_images_sample():
	#from moudle ec2
	ec2.delete_images(region_id="ap-southeast-1",ImageIds=["ami-796ab61a","ami-e76eb284","ami-7e6ab61d"])

def get_instanceids_sample():
	#from moudle ec2
	instances=["KF-Zone-6-Game01-Web-20160718","KF-Zone-6-Portal-Web-20160718","KF-Zone-6-PVP-Web-20160718"]
	instances=ec2.get_instanceids(region_id="ap-southeast-1",InstanceNames=instances)
	# return format [{<InstanceName>:<InatanceId>},{<InstnceName>:None},.....] if None exists means error(Duplicated or NotFound)
	print instances

def create_images_sample():
	#from moudle ec2
	images={"i-5c187cc3":"Cybird-SGK-Android-API-20160803","i-02a7e002ff4233ece":"Cybird-SGK-Android-Web-20160803","i-0b3e35ae8e616d941":"Cybird-SGK-iOS-API-20160803","i-0c6fdeaee7d20d615":"Cybird-SGK-iOS-Web-20160803"}
	images={"i-7a9e6ade":"EMIQ-Mujin-Official-Web-0810"}
	images=ec2.create_images(region_id="ap-northeast-1",InstanceIds_ImageNames=images)
	print images

def fuzzy_search_instances_sample():
	#from moudle ec2
	print ec2.fuzzy_search_instances(region_id="ap-northeast-1",SearchKey="KF-Game\d+-Web")
	# return format [<InstanceName>,<InstanceName>,....]

def get_instancenames_sample():
	#from moudle ec2
	instances=["i-199f9ebc","i-dbbff67e","i-5aa2e9ff","errortest"]
	instances=ec2.get_instancenames(region_id="ap-northeast-1",InstanceIds=instances)
	# return format [{<InstanceName>:<InatanceId>},{<InstnceName>:None},.....] if error instancename key will missing
	names=sorted(instances.values())
	for a in names:
		print a

def fuzzy_search_auto_scaling_groups_sample():
	#from module ec2
	print ec2.fuzzy_search_auto_scaling_groups(region_id="ap-northeast-1",SearchKey="KF-Game\d+-Web")
	# return format [<AutoScalingGroupName>,<AutoScalingGroupName>,....]

def change_auto_scaling_group_size_sample():
	a=autoscaling.change_auto_scaling_group_size("ap-northeast-1","Cybird-SGK-iOS-Web-Group-20160712",0,0)
	a.start()
	a.join()
	print a.groupinfo

def set_auto_scaling_group_instance_name_sample():
	a=autoscaling.set_auto_scaling_group_instance_name("ap-northeast-1","Emiq-Mujin-Official-Web-GRoup-201604013","Emiq-Mujin-Official-Web-Group-20160805")
	a.start()
	a.join()

def add_instance_to_elb_sample():
	a=elb.add_instance_to_elb("ap-northeast-1","ID-FGT","i-5fa2aafd")
	a.start()
	a.join()

def remove_instance_from_elb_sample():
	a=elb.remove_instance_from_elb("ap-northeast-1","ID-FGT","i-5fa2aafd")
	a.start()
	a.join()

def copy_launch_config_sample():
	t=autoscaling.copy_launchconfig(
		"ap-northeast-1",
		"Cybird-SGK-Android-API-Group-201608251543Copy",
		"Cybird-SGK-Android-API-Group-20160830Test",
		"ami-b8e32dd9")
	t.start()
	t.join()

copy_launch_config_sample()

