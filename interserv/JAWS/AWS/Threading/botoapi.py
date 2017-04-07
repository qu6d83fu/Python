import sys
reload(sys)
sys.setdefaultencoding("utf8")
import boto3
import botocore
import time
import random
def safecall(action,**kwargs):
	while True:
		try:
			result=action(**kwargs)
			return result
			break
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']+", Retring"
			time.sleep(random.randint(1,10))