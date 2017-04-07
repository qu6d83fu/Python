from __future__ import print_function
import os
import sys
import json
import ijson
import urllib2

response=urllib2.urlopen("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json")
data=response.read()
format_py=json.loads(data)

if os.path.isfile('price.json'):
  os.remove('price.json')

f1=open('./price.json', 'w')

regions={
        'US East (N. Virginia)':'us-east-1',
        'US West (N. California)':'us-west-1',
        'US West (Oregon)':'us-west-2',
        'EU (Ireland)':'eu-west-1',
        'EU (Frankfurt)':'eu-central-1',
        'Asia Pacific (Tokyo)':'ap-northeast-1',
        'Asia Pacific (Seoul)':'ap-northeast-2',
        'Asia Pacific (Singapore)':'ap-southeast-1  ',
        'Asia Pacific (Sydney)':'ap-southeast-2',
        'Asia Pacific (Mumbai)':'ap-south-1',
        'South America (Sao Paulo)':'sa-east-1'
}

result={}

def JsonDumps(x):
 y=json.dumps(x,sort_keys=True,indent=4)
 return y

def Location(where):
  price={}
  for k in format_py['products']:
    attr=format_py['products'][k]['attributes']
    if format_py['products'][k]["productFamily"]=="Compute Instance":
      if  attr['operatingSystem'] =='Linux':
        if attr['tenancy']=='Shared':
          if attr['location'] ==where:
            PSKU = attr['instanceType']
            if k in format_py['terms']['OnDemand']:
              TSKU=format_py['terms']['OnDemand'][k]
              TTSKU=TSKU[TSKU.keys()[0]]['priceDimensions']
              TTTSKU=TTSKU[TTSKU.keys()[0]]['pricePerUnit']['USD']
              price[PSKU]=TTTSKU
  return price          


for region in regions:
  result.update({regions[region]:Location(region)})
print (JsonDumps(result),file=f1)
  

#for SKU in format_py['products']:
#  ret = {k: v for k, v in format_py.iteritems()  if format_py['products'][SKU]['productFamily']=='Compute Instance' and format_py['products'][SKU]['attributes']['operatingSystem']=='Linux'}

#ret_json=json.dumps(ret,sort_keys =True, indent= 4)
#print (ret, file=f1)
#sys.stdout=open('price.json','ab')
#print json.dumps(ret,sort_keys = True,indent = 4 )

