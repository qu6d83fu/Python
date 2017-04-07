import urllib2
import datetime
import json
import os.path
import boto3
ec2_info=None

def initialize():
    global ec2_info
    #print "test"
    if os.path.exists("./ec2Info.json"):
        ec2_info=json.load(open("./ec2Info.json","r"))
    #    print this.DemandPricing
    else:
        get_update()

def getPricing(region, instance):
    global ec2_info
    #print this.DemandPricing
    if ec2_info==None:
        initialize()
    return float(ec2_info[region][instance]["pricing"])

def getVcpu(region, instance):
    global ec2_info
    #print this.DemandPricing
    if ec2_info==None:
        initialize()
    return float(ec2_info[region][instance]["vcpu"])

def getInfo(region, instance):
    global ec2_info
    #print this.DemandPricing
    if ec2_info==None:
        initialize()
    return float(ec2_info[region][instance])

class _Regions:
    def __init__(self):
        self.regionID={}
        self.regionID["South America (Sao Paulo)"]="sa-east-1"
        self.regionID["US East (N. Virginia)"]="us-east-1"
        self.regionID["US West (Oregon)"]="us-west-2"
        self.regionID["US West (N. California)"]="us-west-1"
        self.regionID["EU (Ireland)"]="eu-west-1"
        self.regionID["EU (Frankfurt)"]="eu-central-1"
        self.regionID["Asia Pacific (Tokyo)"]="ap-northeast-1"
        self.regionID["Asia Pacific (Singapore)"]="ap-southeast-1"
        self.regionID["Asia Pacific (Sydney)"]="ap-southeast-2"
        self.regionID["Asia Pacific (Mumbai)"]="ap-south-1"
        self.regionID["Asia Pacific (Seoul)"]="ap-northeast-2"
    def get(self,regionName):
        try:
            region=self.regionID[regionName]
            return region
        except KeyError:
            return None

def get_update():
    global ec2_info
    ec2_info={}
    if os.path.exists("./version"):
        fo=open("./version","r")
        oldVersion=fo.read()
        fo.close()
    else:
        oldVersion=""
    baseurl="https://pricing.us-east-1.amazonaws.com"
    currenturl="https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json"
    req = urllib2.Request(currenturl)
    response = urllib2.urlopen(req)
    currentInfo=json.loads(response.read())
    versionUrl=currentInfo["offers"]["AmazonEC2"]["versionIndexUrl"]
    req = urllib2.Request(baseurl+versionUrl)
    response = urllib2.urlopen(req)
    verInfo=json.loads(response.read())
    ver=verInfo["currentVersion"]
    if ver==oldVersion:
    #    print "Nothing Change"
        return
    else:
#create dict
        regions=_Regions()
        ec2=boto3.client("ec2")
        allRegions=ec2.describe_regions()["Regions"]
        for r in allRegions:
            ec2_info[r["RegionName"]]={}
#Write version info
        fo=open("./version","w")
        oldVersion=fo.write(ver)
        fo.close()
        offerUrl=baseurl+verInfo["versions"][ver]["offerVersionUrl"]
        req = urllib2.Request(offerUrl)
        response = urllib2.urlopen(req)
        resourceInfo=json.loads(response.read())
        print "Read Complete"
#Start to get region Pricing (Linux only)
        productInfo=resourceInfo["products"]
        demandInfo=resourceInfo["terms"]["OnDemand"]
        infoKeys=productInfo.keys()
        for keyIdx in infoKeys:
            instanceInfo=productInfo[keyIdx]
            try:
                t=instanceInfo["productFamily"]
            except:
                continue
            if instanceInfo["productFamily"] =="Compute Instance":
                instanceAttr=instanceInfo["attributes"]
                if instanceAttr["operatingSystem"] =="Linux" and instanceAttr["tenancy"] == "Shared":
                    regionId=regions.get(instanceAttr["location"])
                    if regionId != None:
                        instanceType=instanceAttr["instanceType"]
                        pricingInfo=demandInfo[keyIdx][demandInfo[keyIdx].keys()[0]]["priceDimensions"]
                        pricing=pricingInfo[pricingInfo.keys()[0]]["pricePerUnit"]["USD"]
                        vcpu=instanceAttr["vcpu"]
                        ec2_info[regionId][instanceType]={"pricing":pricing,"vcpu":vcpu}
        json.dump(ec2_info,open("./ec2Info.json","w"), sort_keys=True, indent=4)
