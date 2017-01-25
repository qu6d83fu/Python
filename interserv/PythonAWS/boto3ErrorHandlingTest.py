import boto3
from AWS.Threading import botoapi
def test():
	ec2=boto3.Session(region_name="ap-northeast-1").client("ec2")
	c=botoapi.safecall(ec2.describe_images,ImageIds=["ami-b8e32dd9"])
	print c

test()
