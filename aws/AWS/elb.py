import boto3
from threading import Thread
import time
import credential

class check_instance_inservice(Thread):
    def __init__(self,region,elb,instance):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('elb')
        self.region=region
        self.elb=elb
        self.instance=instance
    def run(self):
        inservice =False
        while not inservice:
            response=self.client.describe_instance_health(
                    LoadBalancerName=self.elb,
                    Instances=[{'InstanceId': self.instance}])
            if len(response['InstanceStates']) == 1:
                if response['InstanceStates'][0]["State"]=="InService":
                    inservice=True
                else:
                    print 'witing for ELB ' + self.elb + ' ' + self.instance + ' InService'
                    time.sleep(5)
            else:
                print 'witing for ' + self.instance + ' avilible'
                time.sleep(5)
        if inservice:
            print self.elb + ' ' + self.instance + ' InService.'

class deregister_instance_from_elb(Thread):
    def __init__(self,region,elb,instance):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('elb')
        self.region=region
        self.elb=elb
        self.instance=instance
    def run(self):
        response=self.client.deregister_instances_from_load_balancer(
                LoadBalancerName=self.elb,
                Instances=[{'InstanceId': self.instance}])
        t=check_deregister_instance(self.region,self.elb,self.instance)
        t.start()
        t.join()
        print self.elb + ' havs deregister instance ' + self.instance
            
class check_deregister_instance(Thread):
    def __init__(self,region,elb,instance):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('elb')
        self.region=region
        self.elb=elb
        self.instance=instance
    def run(self):
        outservice=False
        while not outservice:
            response = self.client.describe_instance_health(
                LoadBalancerName=self.elb,
                Instances=[{'InstanceId': self.instance}])
            if len(response['InstanceStates'])==1:
                if response['InstanceStates'][0]['State']=='OutOfService':
                    outservice=True
                else:
                    print 'wating for ' + self.instance + ' OutOfService.'
                    time.sleep(5)
            else :
                print 'wating for ' + self.instance + ' OutOfService.'
                time.sleep(5)
            if outservice:
                print self.elb + ' seed instance ' + self.instance + ' is OutOfService'
                break

class add_instance_to_elb(Thread):
    def __init__(self,region,instance,elb):
        Thread.__init__(self)
        self.client=boto3.session.Session(region_name=region).client('elb')
        self.region=region
        self.instance=instance
        self.elb=elb
    def run(self):
        response = self.client.register_instances_with_load_balancer(LoadBalancerName=self.elb,Instances=[{'InstanceId': self.instance}])
        t=check_instance_inservice(self.region,self.elb,self.instance)
        t.start()
        t.join()
