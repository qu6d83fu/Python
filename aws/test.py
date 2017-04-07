import boto3
import AWS.ec2
import AWS.autoscaling
from threading import Thread
import sys
import json
import datetime
filename=sys.argv[1]
x=json.load(open(filename,'r'))
region=x['Region']
servers=x['ServerInfo']
#client=boto3.session.Session(region_name=region).client('autoscaling')
#response = client.describe_launch_configurations(LaunchConfigurationNames=['NA1Copy-201703240211'])['LaunchConfigurations'][0]
#print response 

newimg='ami-b6d883d1'
t=AWS.ec2.get_image_mappings(region,newimg)
t.start()
t.join()
i= t.imgmapping
print i
#for a in servers:
#    groupname=a['AutoScalingGroup']
#    t=copy_launch_configuration(region,groupname,newimg)
#    t.start()
#    t=AWS.autoscaling.update_auto_scaling_group(region,groupname,'NA1Copy-201703240342')
#    t.start()

