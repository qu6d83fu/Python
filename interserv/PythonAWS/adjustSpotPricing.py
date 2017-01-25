import boto3
import datetime
import json
from AWS import ec2_info
from threading import Thread
from AWS.Threading import botoapi
#import os.path
class ec2SpotBidHistory:
    def __init__(self):
         self.bidHistory={}
         ec2=boto3.client("ec2")
         allRegions=botoapi.safecall(ec2.describe_regions)["Regions"]
         for r in allRegions:
             self.bidHistory[r["RegionName"]]={}
            
    def get(self,region,instanceType):
        try:
            bid=self.bidHistory[region][instanceType]
        except KeyError:
            bid=None
        return bid
    
    def set(self,region,instanceType,bidPricing,az):
        self.bidHistory[region][instanceType]={"az":az,"bid":bidPricing}

class subnetIDs:
    def __init__(self):
        self._subnets={}

    def get(self,az):
        try:
            subid=self._subnets[az]
        except KeyError:
            region_id=az[0:len(az)-1]
            ec2Client=boto3.Session(region_name=region_id).client("ec2")
            subnets=botoapi.safecall(ec2Client.describe_subnets)["Subnets"]
            for s in subnets:
                if s["AvailabilityZone"]==az:
                    self._subnets[az]=s["SubnetId"]
            subid=self._subnets[az]
        return subid




def copyLaunchConfig(session,launchInfo,newbid):
    scalingClient=session.client("autoscaling")
    newName= launchInfo["LaunchConfigurationName"].split("-")
    newName.pop()
    newName.append(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    newName="-".join(newName)
    imageID=launchInfo["ImageId"]
    keyName=launchInfo["KeyName"]
    securityGroups=launchInfo["SecurityGroups"]
    userData=launchInfo["UserData"]
    instanceType=launchInfo["InstanceType"]
    kernelID=launchInfo["KernelId"]
    ramDiskID=launchInfo["RamdiskId"]
    blockDeviceMappings=launchInfo["BlockDeviceMappings"]
    instanceMonitoring=launchInfo["InstanceMonitoring"]
    spotPrice=str(newbid)
    ebsOptimized=launchInfo["EbsOptimized"]
    botoapi.safecall(
        scalingClient.create_launch_configuration,
        LaunchConfigurationName=newName,
        ImageId=imageID,
        KeyName=keyName,
        UserData=userData,
        SecurityGroups=securityGroups,
        InstanceType=instanceType,
        BlockDeviceMappings=blockDeviceMappings,
        InstanceMonitoring=instanceMonitoring,
        SpotPrice=spotPrice,
        EbsOptimized=ebsOptimized)
    return newName


class adjustSpotPricing(Thread):
    def __init__(self,regionid):
        Thread.__init__(self)
        self.regionid=regionid
   
    def run(self):
        global subnets
        global bidHistory
        session=boto3.Session(region_name=self.regionid)
        scalingClient=session.client("autoscaling")
        ec2Client=session.client("ec2")
        spotError=botoapi.safecall(
            ec2Client.describe_spot_instance_requests,
            Filters=[{"Name":"status-code","Values":["price-too-low"]}])["SpotInstanceRequests"]
        if len(spotError)>0:
            forceUpdate=True
        else:
            forceUpdate=False;
        #print forceUpdate

        nextToken=None
        while nextToken!= "":
            if nextToken==None:
                scalingInfo=botoapi.safecall(scalingClient.describe_auto_scaling_groups,
                    MaxRecords=1)
            else:
                scalingInfo=botoapi.safecall(scalingClient.describe_auto_scaling_groups,
                    NextToken=nextToken
                    ,MaxRecords=1)
            groupName=scalingInfo["AutoScalingGroups"]
            if len(groupName)==0:
                nextToken=""
                continue
            groupName=groupName[0]["AutoScalingGroupName"]
            launchName=scalingInfo["AutoScalingGroups"][0]["LaunchConfigurationName"]
            launchInfo=botoapi.safecall(scalingClient.describe_launch_configurations,
                LaunchConfigurationNames=[launchName])["LaunchConfigurations"][0]
            #print groupName
            try:
                oldbid=float(launchInfo["SpotPrice"])
            except KeyError:
                oldbid=None
                #print "Not a Spot LauhchConfigure"
            if oldbid!=None:
                #print "oldbid="+str(oldbid)
                instanceType=launchInfo["InstanceType"]
                #assume all AutoScaling groups use the same availabilityZones, if not set them to the same. 
                elbName=scalingInfo["AutoScalingGroups"][0]["LoadBalancerNames"][0]
                elbClient=session.client("elb")
                elbInfo=elbClient.describe_load_balancers(LoadBalancerNames=[elbName])
                AZ=elbInfo["LoadBalancerDescriptions"][0]["AvailabilityZones"]
                regionID=AZ[0]
                regionID=regionID[0:len(regionID)-1]
                bestbid=bidHistory.get(regionID,instanceType)
                if bestbid==None:
                    maxbid= ec2_info.getPricing(regionID,instanceType)
                    #print "instanceType="+instanceType+",maxbid="+str(maxbid)
                    now=datetime.datetime.utcnow()
                    start=now-datetime.timedelta(minutes=10)
                    now=now.isoformat()
                    start=start.isoformat()
                    curPricing={}
                    maxPricing={}
                    for az in AZ:
                        maxtemp=0.0
                        curtemp=0.0
                        #print az
                        priceResult=botoapi.safecall(ec2Client.describe_spot_price_history,
                            StartTime=start,
                            EndTime=now,
                            InstanceTypes=[instanceType],
                            ProductDescriptions=["Linux/UNIX"],
                            AvailabilityZone=az)["SpotPriceHistory"]                
                        #print priceResult
                        for price in priceResult:
                            p=float(price["SpotPrice"])
                            if curtemp==0.0:
                                curPricing[az]=p
                            if maxtemp<p:
                                maxtemp=p
                        maxPricing[str(maxtemp)]=az
                    maxAz=maxPricing[str(min(maxPricing))]
                    curPricing=float(curPricing[maxAz])
                    maxPricing=float(min(maxPricing))
                    #print "maxbid="+str(maxbid)
                    if oldbid>maxbid or oldbid<curPricing or oldbid/maxPricing>1.5 or forceUpdate:
                        bestbid=maxPricing*1.2
                        #print "bestbid1="+str(bestbid)
                        if bestbid>maxbid:
                            bestbid=curPricing*1.2
                            #print "bestbid2="+str(bestbid)
                            if bestbid>maxbid: 
                                bestbid=maxbid
                                #print "bestbid3="+str(bestbid)
                    else:
                        bestbid=oldbid
                    bidHistory.set(regionID,instanceType,bestbid,maxAz)
                    #print "bestbid="+str(bestbid)
                else:
                    maxAz=bestbid["az"]
                    bestbid=bestbid["bid"]
                #print instanceType
                #print "curPricing="+str(curPricing)
                #print "maxPricing="+str(maxPricing)
                print "Az="+maxAz
                if bestbid!=oldbid:
                    newLaunchName=copyLaunchConfig(session,launchInfo,bestbid)
                    #print newLaunchName
                    #print maxAz
                    scalingClient.update_auto_scaling_group(
                        AutoScalingGroupName=groupName,
                        LaunchConfigurationName=newLaunchName,
                        VPCZoneIdentifier=subnets.get(maxAz),
                        AvailabilityZones=[maxAz])
                    scalingClient.delete_launch_configuration(
                        LaunchConfigurationName=launchName)



                if forceUpdate:
                    #even launched instance will be terminated in one minuts, don't close it by yourself
                    #terminated by aws system will not require to pay
                    #also, it will clear spot request list
                    minSize=0
                    for i in scalingInfo["AutoScalingGroups"][0]["Instances"]:
                        #print i["LifecycleState"]
                        if i["LifecycleState"] in "Pending:Wait Pending:Proceed InService EnteringStandby":
                            minSize+=1
                    if minSize<scalingInfo["AutoScalingGroups"][0]["MinSize"]:
                        minSize=scalingInfo["AutoScalingGroups"][0]["MinSize"]

                    botoapi.safecall(
                        scalingClient.update_auto_scaling_group,
                        AutoScalingGroupName=groupName,
                        DesiredCapacity=minSize)

            try:
                nextToken=scalingInfo["NextToken"]
            except KeyError:
                nextToken=""


def adjustAllRegionSpotPricing():
    allRegions=["sa-east-1","us-east-1","us-west-2","us-west-1","eu-west-1","eu-central-1","ap-northeast-1","ap-southeast-1","ap-southeast-2","ap-south-1","ap-northeast-2"]
    #allRegions=["ap-northeast-1"]
    for r in allRegions:
        print r
        adjust=adjustSpotPricing(r)
        adjust.start()

subnets=subnetIDs()
bidHistory=ec2SpotBidHistory()
adjustAllRegionSpotPricing() 

