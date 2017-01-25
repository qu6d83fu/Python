import boto3
import datetime
from AWS.Threading import botoapi
class getImageSnapshot:
	def __init__(self,region_id):
		self.snapshots=[]
		ec2Client=boto3.Session(region_name=region_id).client("ec2")
		allImages=botoapi.safecall(ec2Client.describe_images,Owners=["936354427014"])["Images"]
		for i in allImages:
			for s in i["BlockDeviceMappings"]:
				self.snapshots.append(s["Ebs"]["SnapshotId"])

	def exists(self,snapshotID):
		return snapshotID in self.snapshots

def cleanUpSnapshots(region_id):
	ec2Client=boto3.Session(region_name=region_id).client("ec2")
	nextToken=None
	usedSnapshots=getImageSnapshot(region_id)
	while nextToken!= "":
		if nextToken==None:
			snapshots=botoapi.safecall(ec2Client.describe_snapshots,OwnerIds=["936354427014"],MaxResults=10)
		else:
			snapshots=botoapi.safecall(ec2Client.describe_snapshots,OwnerIds=["936354427014"],MaxResults=10,NextToken=nextToken)
			oldToken=nextToken
		partSnapshots=snapshots["Snapshots"]
		for s in partSnapshots:
			#print s["SnapshotId"]
			if not usedSnapshots.exists(s["SnapshotId"]):
				#not used for AMI
				hasName=True
				try:
					t=s["Tags"]
				except KeyError:
					hasName=False
				if hasName:
					hasName=False
					for t in s["Tags"]:
						if "Name" == t["Key"] and t["Value"]!='':
							hasName=True
							#print hasName
							break
				if not hasName:
					botoapi.safecall(ec2Client.delete_snapshot,DryRun=False,SnapshotId=s["SnapshotId"])
					print s["SnapshotId"]+" deleted"			
		try:
			nextToken=snapshots["NextToken"]
		except KeyError:
			nextToken=""

def cleanUpAllRegionsSnapshots():
	ec2Client=boto3.client("ec2")
	allRegions=ec2Client.describe_regions()["Regions"]
	for r in allRegions:
		#print r["RegionName"]
		cleanUpSnapshots(r["RegionName"])

cleanUpAllRegionsSnapshots()

