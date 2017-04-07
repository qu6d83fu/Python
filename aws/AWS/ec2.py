import boto3
from threading import Thread
import time
import credential
global imgids
imgids={}
class get_instance_names(Thread):
    def __init__(self,region,instanceid):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('ec2')
        self.instanceid=instanceid
        self.instancename=None
    def run(self):
        response=self.client.describe_instances(Filters=[{'Name': 'instance-id','Values': [self.instanceid]}])['Reservations']
        if len(response) == 1:
            for i in response[0]['Instances']:
                for t in i['Tags']:
                    if t['Key'] == 'Name':
                        self.instancename=t['Value']
        else:
            self.instancename='None'

class create_images(Thread):
    def __init__(self,region,instanceid,imgname):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('ec2')
        self.instanceid=instanceid
        self.imgname=imgname
    def run(self):
        imgid = self.client.create_image(
        InstanceId=self.instanceid,
        Name=self.imgname,
        Description='Create from instanceid' + self.instanceid,
        NoReboot=True)["ImageId"]
        while True:
            time.sleep(5)
            state=self.client.describe_images(
                ImageIds=[imgid])["Images"][0]["State"]
            if state =='available':
                print self.imgname + ' image have created.'
                self.imgid=imgid
                break
            elif state =='pending':
                print 'Wating for creating image ' + self.imgname
                pass
            else:
                print 'Some error occuring on image ' + self.imgname
                imgids[self.imgname]='error'
                self.imgid=None
                break

class get_image_mappings(Thread):
    def __init__(self,region,img):
        self.client=boto3.session.Session(region_name=region).client('ec2')
        Thread.__init__(self)
        self.region=region
        self.img=img
        self.imgmapping=None
        self.snapshots=[]
    def run(self):
        self.imgmapping=self.client.describe_images(ImageIds=[self.img])['Images'][0]['BlockDeviceMappings']
        for e in self.imgmapping:
            self.snapshots.append(e['Ebs']['SnapshotId'])
            
class deregister_images(Thread):
    def __init__(self,region,oldimg):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('ec2')
        self.region=region
        self.oldimg=oldimg
    def run(self):
        t = get_image_mappings(self.region,self.oldimg)
        t.start()
        t.join()
        snapshots=t.snapshots
        response = self.client.deregister_image(ImageId=self.oldimg)
        print self.oldimg + ' have been deregisted.'
        thread=[]
        for s in snapshots:
            t=delete_snapshots(self.region,s,self.oldimg)
            t.start()
            thread.append(t)
        for t in thread:
            t.join()

class delete_snapshots(Thread):
    def __init__(self,region,snapshot,oldimg):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('ec2')
        self.snapshot=snapshot
        self.oldimg=oldimg
    def run(self):
        response = self.client.delete_snapshot(SnapshotId=self.snapshot)
        print self.oldimg + ' ' + self.snapshot + ' have been deleted.'
