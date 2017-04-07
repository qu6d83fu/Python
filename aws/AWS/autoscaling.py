#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import boto3
import ec2
import time
import datetime
from threading import Thread
import credential
global failgroupnames
failgroupnames=[]
class check_auto_scaling_group_exist(Thread):
    def __init__(self,region,groupname):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('autoscaling')
        self.groupname=groupname
        self.exist=False
    def run(self):
        response=len(self.client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.groupname])['AutoScalingGroups'])
        if response  == 1:
            self.exist=True
        else :
            self.exist=False
            failgroupnames.append(self.groupname)

class change_auto_scaling_group_size(Thread):
    def __init__(self,region,groupname,min,desired):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('autoscaling')
        self.region=region
        self.groupname=groupname
        self.min=min
        self.desired=desired
        self.instanceids=[]
    def run(self):
        response = self.client.update_auto_scaling_group(AutoScalingGroupName=self.groupname,DesiredCapacity=self.desired)
        while True:
            self.instanceids=[]
            t=get_auto_scaling_groups(self.region,self.groupname)
            t.start()
            t.join()
            self.elbs=t.elbs
            ready=False
            if len(t.response['Instances'])==self.desired:
                ready=True
                for i in t.response['Instances']:
                    self.instanceids.append(i["InstanceId"])
                    if i['LifecycleState'] != 'InService':
                        print 'ASG ' + self.groupname + ' waiting for instance InService'
                        ready=False
                        break
            if ready:
                print 'ASG ' + self.groupname + ' instances have been changed to ' + str(self.desired)
                break
            time.sleep(5)

class get_auto_scaling_groups(Thread):
    def __init__(self,region,groupname):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('autoscaling')
        self.groupname=groupname
        self.state=False
        self.response=None
    def run(self):
        self.response = self.client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.groupname])['AutoScalingGroups'][0]
        self.launchconfig=self.response["LaunchConfigurationName"]
        self.elbs=self.response["LoadBalancerNames"]
        self.desired=self.response["DesiredCapacity"]

class copy_launch_configuration(Thread):
    def __init__(self,region,groupname,newimg):
        self.client=boto3.session.Session(region_name=region).client('autoscaling')
        Thread.__init__(self)
        self.region=region
        self.groupname=groupname
        self.newimg=newimg
    def run(self):
        oldlaunchconfig = self.client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.groupname])['AutoScalingGroups'][0]['LaunchConfigurationName']
        self.oldlaunchconfig=oldlaunchconfig
        t=ec2.get_image_mappings(self.region,self.newimg)
        t.start()
        t.join()
        imgmapping=t.imgmapping
        for i in imgmapping:
            i['Ebs'].pop('Encrypted',None)

        response = self.client.describe_launch_configurations(LaunchConfigurationNames=[oldlaunchconfig])['LaunchConfigurations'][0]
        newlaunchconfig=response['LaunchConfigurationName']
        newlaunchconfig=newlaunchconfig.split("-")
        newlaunchconfig.pop()
        newlaunchconfig=newlaunchconfig+[unicode(datetime.datetime.now().strftime("%Y%m%d%H%M"),"utf-8")]
        newlaunchconfig=u"-".join(newlaunchconfig)
        self.newlaunchconfig=newlaunchconfig
        self.oldimg=response['ImageId']
        keyname=response['KeyName']
        securitygroups=response['SecurityGroups']
        instancetype=response['InstanceType']
        response = self.client.create_launch_configuration(
        LaunchConfigurationName=newlaunchconfig,
        ImageId=self.newimg,
        KeyName=keyname,
        SecurityGroups=securitygroups,
        InstanceType=instancetype,
        BlockDeviceMappings=imgmapping,
        InstanceMonitoring={
            'Enabled': False
        },
        EbsOptimized=False,
)

class update_auto_scaling_group(Thread):
    def __init__(self,region,groupname,launchconfig,imgname):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('autoscaling')
        self.region=region
        self.groupname=groupname
        self.launchconfig=launchconfig
        self.imgname=imgname
    def run(self):
        response = self.client.update_auto_scaling_group(
            AutoScalingGroupName=self.groupname,
            LaunchConfigurationName=self.launchconfig,
            )
        t=update_auto_scaling_group_tag(self.region,self.groupname,self.imgname)
        t.start()
        t.join()
        print 'ASG ' + self.groupname + ' have updated'

class update_auto_scaling_group_tag(Thread):
    def __init__(self,region,groupname,imgname):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('autoscaling')
        self.region=region
        self.groupname=groupname
        self.imgname=imgname
    def run(self):
        response = self.client.create_or_update_tags(
        Tags=[
            {
                'ResourceId': self.groupname,
                'ResourceType': 'auto-scaling-group',
                'Key': 'Name',
                'Value': self.imgname + '-temp',
                'PropagateAtLaunch': True
            },
            ]
        )

class delete_launchconfig(Thread):
    def __init__(self,region,launchconfig):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('autoscaling')
        self.region=region
        self.launchconfig=launchconfig
    def run(self):
        response = self.client.delete_launch_configuration(LaunchConfigurationName=self.launchconfig)
        print 'launchconfig ' + self.launchconfig + ' have deleted.'
