import boto3
import fnmatch
import time
import json
ec2client=boto3.client('autoscaling')
confname=raw_input('Enter launChconfig name ')
response = ec2client.describe_launch_configurations(
    LaunchConfigurationNames=[
        confname,
    ],
#   NextToken='123',
    MaxRecords=100
)
print response

'''
response = ec2client.create_launch_configuration(
    LaunchConfigurationName='string',
    ImageId='string',
    KeyName='string',
    SecurityGroups=[
        'string',
    ],
    ClassicLinkVPCId='string',
    ClassicLinkVPCSecurityGroups=[
        'string',
    ],
    UserData='string',
    InstanceId='string',
    InstanceType='string',
    KernelId='string',
    RamdiskId='string',
    BlockDeviceMappings=[
        {
            'VirtualName': 'string',
            'DeviceName': 'string',
            'Ebs': {
                'SnapshotId': 'string',
                'VolumeSize': 123,
                'VolumeType': 'string',
                'DeleteOnTermination': True|False,
                'Iops': 123,
                'Encrypted': True|False
            },
            'NoDevice': True|False
        },
    ],
    InstanceMonitoring={
        'Enabled': True|False
    },
    SpotPrice='string',
    IamInstanceProfile='string',
    EbsOptimized=True|False,
    AssociatePublicIpAddress=True|False,
    PlacementTenancy='string'
)
'''
