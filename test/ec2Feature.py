import boto3
import argparse

class ec2Feature:
    def __init__(self):
        self.ec2client = boto3.client('ec2')
        self.ec2resource = boto3.resource('ec2')
        self.autoclient = boto3.client('autoscaling')
    def ec2InstanceID(self):
        self.instance=self.ec2client.describe_instances()
        num=0
        while True:
            try:
                instanceID=self.instance['Reservations'][num]['Instances'][0]['InstanceId']
            except IndexError:
                break
            if instanceID !=  None:
                instanceTag=self.instance['Reservations'][num]['Instances'][0]['Tags'][0]['Value']
                print "Key = Name,Value = %s  \tInstance ID = %s" %(instanceTag,instanceID)
                num += 1
    
    def ec2ChangeTag(self):
        instanceID =''
        tagValue=''
        while not instanceID:
            instanceID=raw_input('Enter the instance id: ')

        while not tagValue:
            tagValue=raw_input('Enter the Tag value: ')
        
        instance = self.ec2resource.Instance(instanceID)

        describe=instance.describe_attribute(
            DryRun=False,
            Attribute='blockDeviceMapping'
        )   
        
        volumeID=describe['BlockDeviceMappings'][0]['Ebs']['VolumeId']
        
        volumeResource=self.ec2resource.Volume(volumeID)
        volumeTagCreate=volumeResource.create_tags(
        DryRun=False,
        Tags=[
            {
                'Key':'Name',
                'Value':tagValue
            },
            ]
        )

        instanceResource=self.ec2resource.Instance(instanceID)
        instanceTagCreate=instanceResource.create_tags(
        DryRun=False,
        Tags=[
            {
                'Key':'Name',
                'Value':tagValue
            },
            ]
        )
'''
        def autoscalingAddInstance(self):
            autoscaling=self.autoclient.attach_instances(
            InstanceIds=[
                '',
            ],
            )
'''
    
#NUMBER=['1','2','3']
def get_args(args):
    parser = argparse.ArgumentParser(add_help=True, description="AWS Server Tool")
#    parser.add_argument("--show-number", "-sn", help="show number of function", choices=NUMBER, default=None)
    parser.add_argument("--show-instance", help="Show instances tag and id", action="store_true")
    parser.add_argument("--change-tag", help="Change tag name", action="store_true")
    args = parser.parse_args(args=args)
    return args

if get_args(None).show_instance:
    ec2Feature().ec2InstanceID()
if get_args(None).change_tag:
    ec2Feature().ec2ChangeTag()


'''
parameter=get_args(None).show_number

def showFunction(number):
    if number == '1':
        print 'life is good'
    elif number == '2':
        print 'mabe you need some flavor that make your life colorful'
    elif number == '3':
        print 'Don\'t waste your life just do it'

showFunction(parameter)
'''
