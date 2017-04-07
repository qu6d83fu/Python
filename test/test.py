import boto3
import botocore
import fnmatch
import time

elb=boto3.client('elb')
autoscaling= boto3.client("autoscaling") 
ec2client = boto3.client("ec2")
ec2resource = boto3.resource("ec2")

image=ec2resource.Image('ami-a0549cc1')
snapshot=ec2resource.Snapshot('snap-864137b9')
elbname='test'

def change_desired_number(autoname,desire,elbname):
    autocapacity=autoscaling.set_desired_capacity(
        AutoScalingGroupName=autoname,
        DesiredCapacity=desire,
        HonorCooldown=True
    )
    if desire > 0:
        print 'waite new instance add to elb... '
        while True:
            elb_num=len(check_elb_instance_list(elbname))
            if elb_num >= 2:
                print 'desire instance OnService'
                break
            else:
                print 'waiting instance launch'
                time.sleep(30)


def check_elb_instance_list(elbname):
    num=0
    global elb_instance_list
    elb_instance_list=[]
    while True:
        try:
            elb_instance_id=elb.describe_load_balancers(
            LoadBalancerNames=[
                elbname,
            ],
        #    Marker='',
        #    PageSize=
        )['LoadBalancerDescriptions'][0]['Instances'][num]['InstanceId']
        except IndexError:
            num += 1
            break
        elb_instance_list.append(elb_instance_id)
        num += 1
    return elb_instance_list

def search_instance_tag(elbinstanceid):
    num=0
    while True:
        try:
            instanceid=ec2client.describe_instances()['Reservations'][num]['Instances'][0]['InstanceId']
        except IndexError:
            break
        if instanceid ==  elbinstanceid:
            instancetag=ec2client.describe_instances()['Reservations'][num]['Instances'][0]['Tags'][0]['Value']
            return instancetag
            num += 1
        else:
            num += 1

def deregister_elb_instance(elbname,instanceid):
    deregister=elb.deregister_instances_from_load_balancer(
    LoadBalancerName=elbname,
    Instances=[
        {
            'InstanceId': instanceid
        },
        ]
    )

def register_elb_instance(elbname,instanceid):
    register = elb.register_instances_with_load_balancer(
    LoadBalancerName=elbname,
    Instances=[
        {
            'InstanceId': instanceid
        },
        ]
    )

def elb_instance_health(elbname,instance):
    elbhealth=elb.describe_instance_health(
                        LoadBalancerName=elbname,
                        Instances=[
                            {
                                'InstanceId': instance
                            },
                            ]
                        )['InstanceStates'][0]['State']
    return elbhealth

def create_image(instanceid):
    createimage=ec2client.create_image(
    #    DryRun=True|False,
        InstanceId=instanceid,
        Name='NewImage',
        Description=instanceid,
        NoReboot=True,
    )['ImageId']
    return createimage

def create_image_tag(ami_id,value):
    image=ec2resource.Image(ami_id)
    imagetag=image.create_tags(
        DryRun=False,
        Tags=[
            {
                'Key': 'Name',
                'Value': value
            },
        ]
    )

def create_image_snapshot_tag(snap_id,value):
    snapshot=ec2resource.Snapshot(snap_id)   
    snapshottag = snapshot.create_tags(
        DryRun=False,
        Tags=[
            {
                'Key': 'Name',
                'Value': value
            },
        ]
    )
def image_snapshot_id(ami_id):
    snapshotid = ec2client.describe_images(
    DryRun=False,
    ImageIds=[
        ami_id,
    ]
    )['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
    return snapshotid

def create_image_flow():
    ami_id=create_image('i-029939f4a97b06889')
    create_image_tag(ami_id,'Game01')
    time.sleep(5)
    snap_id=image_snapshot_id(ami_id)
    create_image_snapshot_tag(snap_id,'Game01')

def check_elb_instance_status(elbname): 
    num=0
    while True:
        try:
            instancetag=ec2client.describe_instances()['Reservations'][num]['Instances'][0]['Tags'][0]['Value']
        except IndexError:
            break
        if fnmatch.fnmatch(instancetag,'KF-Game*'):
            instanceid=ec2client.describe_instances()['Reservations'][num]['Instances'][0]['InstanceId']

            for elbinstance in elbinstancelist:
                if elbinstance != instanceid:
                    try:
                        elb_instance_health(elbname,elbinstance)
                    except botocore.exceptions.ClientError :
                        elbhealth=None
                    print '%s:%s' %(elbinstance,elbhealth)
                    while True:
                        if elbhealth == 'InService':
                            deregister_elb_instance(elbname,instanceid)
                            break
                
            num += 1
        else:
            num += 1        

'''
def main():
#    autoname=raw_input('Enter autoscaling name ')
#    desire=int(raw_input('Enter desired instance number '))
#    change_desired_number(autoname,desire,elbname) 
#    check_elb_instance_list(elbname)
#    for x in elb_instance_list:
#        print 'ELB_Instance:%s,Tag:%s' %(x,search_instance_tag(x))    
    register_elb_instance(elbname,'i-029939f4a97b06889')
    print check_elb_instance_list(elbname)


if __name__ == '__main__':
    main()
'''
'''
#Enter Game server name
num=0
while True:
    try:
        instancetag=ec2client.describe_instances()['Reservations'][num]['Instances'][0]['Tags'][0]['Value']
    except IndexError:
        break
    if fnmatch.fnmatch(instancetag,'KF-Game*'):
        instanceid=ec2client.describe_instances()['Reservations'][num]['Instances'][0]['InstanceId']
        #Mabe can use a dictionary .....to be continued

        try:
            elbname=raw_input('Enter the elb name ')
            elbhealth=elb.describe_instance_health(
            LoadBalancerName=elbname,
            Instances=[
                {
                    'InstanceId': instanceid
                },
                ]
            )['InstanceStates'][0]['State']
        except botocore.exceptions.ClientError :
            elbhealth=None
        print '%s:%s:%s' %(instancetag,instanceid,elbhealth)        
        num += 1
    else:
        num += 1
'''


