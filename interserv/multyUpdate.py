import threading
import subprocess
import shlex
import sys
import os
import time

serverlist={}
lock=threading.Lock()
#Number of server of region
regionnum={'NA':3,'SEA':5}
#regionnum={'na':3,'sea':7}
regionname=['NA','SEA','ALL']
#md5filename
md5file='idsea'
md5name=''

class connectTest(threading.Thread):
        def __init__(self,ip):
                super(connectTest,self).__init__()
                self.ip=ip
        def run(self):
                subprocess.call("ssh centos@{0} 'date'".format(self.ip),shell=True)

class copyOnlineConfig(threading.Thread):
        def __init__(self,region,regionnum,regionname,count,ip,num):
                super(copyOnlineConfig,self).__init__()
                self.region=region
                self.regionnum=regionnum
                self.regionname=regionname
                self.count=count
                self.ip=ip
                self.num=num
        def run(self):
		print "Region {0} Game {1}".format(self.regionname[self.region],self.count)
                subprocess.call('scp -i /root/.ssh/finished.pem centos@{0}:~/id/Game_{1}/Game/Game/settings/local.py /opt/awsOnline/onlineServer_bak/{2}/group_01/game_00{3}/Game/Game/settings/local.py'.format(self.ip,self.num,self.regionname[self.region],self.count),shell=True)
                subprocess.call('scp -i /root/.ssh/finished.pem centos@{0}:~/id/Game_{1}/Game/Game/settings/base.py /opt/awsOnline/onlineServer_bak/{2}/group_01/game_00{3}/Game/Game/settings/base.py'.format(self.ip,self.num,self.regionname[self.region],self.count),shell=True)
#                print "Region {0} Game {1}".format(self.regionname[self.region],self.count)

def serverIP(region):
	count=1
	serverlist[region]=list()
	print '-----region name {0}-----'.format(regionname[region])
        while count<=regionnum[regionname[region]]:
                filepath="/opt/awsOnline/onlineServer_bak/{0}/group_01/game_00{1}/fab/conf.py".format(regionname[region],count)
                f=open(filepath,"r")
                for line in f:
                        if "dict" in line:
                                p1=subprocess.Popen(shlex.split('cat %s'%(filepath)),stdout=subprocess.PIPE)
                                p2=subprocess.Popen(shlex.split('grep Hosts\ ='),stdin=p1.stdout,stdout=subprocess.PIPE)
                                p3=subprocess.Popen(shlex.split("awk -F'@' '{print $2}'"),stdin=p2.stdout,stdout=subprocess.PIPE)
                                p4=subprocess.Popen(shlex.split("awk -F':' '{print $1}'"),stdin=p3.stdout,stdout=subprocess.PIPE).communicate()[0].strip()
                                print p4
				serverlist[region].append(p4)
		f.close()
                count +=1

class svnUpdate(threading.Thread):
        def __init__(self,region,count,version,singlepath,regionname,lock):
                super(svnUpdate, self).__init__()
                self.region=region
                self.count=count
                self.version=version
                self.singlepath=singlepath
                self.regionname=regionname
                self.lock=lock
        def run(self):
#		self.lock.acquire()
		filepath="/opt/awsOnline/onlineServer_bak/%s/group_01/game_00%s/Game" %(self.regionname[self.region],self.count)
		if self.version == '':
                	subprocess.call(shlex.split("svn update {0}{1}{2}".format(self.version,filepath,self.singlepath)))
                else:
                	subprocess.call(shlex.split("svn update -r{0} {1}{2}".format(self.version,filepath,self.singlepath)))
#		self.lock.release()

class deployServer(threading.Thread):
        def __init__(self,region,regionname,count,lock):
                super(deployServer, self).__init__()
		self.region=region
		self.regionname=regionname
		self.count=count
                self.lock=lock

        def run(self):
#               self.lock.acquire()
                filepath="/opt/awsOnline/onlineServer_bak/%s/group_01/game_00%s/fab" %(self.regionname[self.region],self.count)
                subprocess.call('fab stopAll installService deployServer startAll > /opt/awsOnline/updatelog/{0}_{1}_$(date +%Y%m%d%H%M%S).log'.format(self.regionname[self.region],self.count),shell=True,cwd='{0}'.format(filepath))
#               self.lock.release()

class md5Upload(threading.Thread):
        def __init__(self,ip,md5file,regionname,region,count,lock):
                super(md5Upload, self).__init__()
                self.ip=ip
                self.md5file=md5file
		self.regionname=regionname
		self.region=region
                self.count=count
                self.lock=lock
        def run(self):
		global md5name
		self.lock.acquire()
                p1=subprocess.Popen(shlex.split('find /root/MD5File/ -maxdepth 1 -name {0}*.md5'.format(self.md5file)),stdout=subprocess.PIPE)
                p2=subprocess.Popen(shlex.split("awk -F'MD5File/' '{print $2}'"),stdin=p1.stdout,stdout=subprocess.PIPE).communicate()[0].strip()
		md5name=p2
                subprocess.call(shlex.split("scp -i /root/.ssh/finished.pem /root/MD5File/{0} centos@{1}:~/".format(p2,self.ip)))
                subprocess.call(shlex.split("ssh -i /root/.ssh/finished.pem  centos@{0} \"sh ~/md5check.sh\" {1} {2}".format(self.ip,p2,self.count)))
                print "--------{0} {1} IP:{2} finished compare--------\nEnter and continue: \n".format(self.regionname[self.region],self.count,self.ip)
		self.lock.release()

#Show region name
i=0
while True:
	try:
		if regionname[i] not in "":
			print '{0}.{1}'.format(i,regionname[i])
		i+=1
	except IndexError:
        	break

#Chose region
region=input("Chose region number: ")
if region == 0 or region == 1:
	serverIP(region)
elif region == 2:
	for x in range(2):
		serverIP(x)
else:
	print 'Wrong paramet'
	sys.exit()

print serverlist

#connect test
thread=[]
print 'Start ssh testing... '
if region == 0 or region == 1:
	for ip in serverlist[region]:
		t=connectTest(ip)
		t.start()
		thread.append(t)
	for t in thread:
		t.join()
elif region == 2:
	for y in range(2):
		for ip in serverlist[y]:
			t=connectTest(ip)
			t.start()
			thread.append(t)
		for t in thread:
			t.join()

#Chose single svn file or all file
pattern=raw_input("Single file update (y/N): ")
if pattern == 'y' or pattern == 'Y':
    singlepath=raw_input("file path(/settings/local.py): ")
    print 'single file'

elif pattern == 'n' or pattern == 'N' or pattern == '':
    print 'all file'
    singlepath=''

#Enter svn version
svncheck=0
svnskip=0
while svncheck == 0 :
    verpattern=raw_input("Sepcific svn version (y/n/Skip): ")
    if verpattern == 'y' or verpattern =='Y':
        version=raw_input("Enter the version: ")
        vercheck=raw_input('Is version {0} correct (y/N): '.format(version))
	while True:
		if vercheck == 'n' or vercheck == 'N' or vercheck == '':
			version=raw_input("Enter the version: ")
			vercheck=raw_input('Is version {0} correct (y/N): '.format(version))
		elif vercheck == 'y' or vercheck == 'Y':
			break
		else :
			print 'Wrong paramet'
			sys.exit()
        svncheck=1
    elif verpattern == 'n' or verpattern == 'N' :
        version=''
        svncheck=1
    elif verpattern == 's' or verpattern == 'S' or verpattern == 'Skip' or verpattern =='':
        print 'Skip svn update'
        svncheck=1
        svnskip=1

#svn update
if svnskip == 0:
        if region == 0 or region == 1:
		thread = []
		count = 1
		while count <= regionnum[regionname[region]]:
			t=svnUpdate(region,count,version,singlepath,regionname,lock)
			t.start()
			thread.append(t)
			count += 1
		for t in thread:
			t.join()
	
	elif region == 2:
		for x in range(2):
			thread = []
			count = 1
			while count <= regionnum[regionname[x]]:
				t=svnUpdate(x,count,version,singlepath,regionname,lock)
				t.start()
				thread.append(t)
				count += 1
		for t in thread:
			t.join()

#copy online config
checkcopyconfig=raw_input('Copy online config to QA server? (y/N): ')
if checkcopyconfig == 'y' or checkcopyconfig == 'Y':
	thread=[]
	if region == 0 or region == 1:
		count=1
        	a=serverlist[region]
        	b=range(1,regionnum[regionname[region]]+1)
		for ip,num in zip(a,b):
        		t=copyOnlineConfig(region,regionnum,regionname,count,ip,num)
			t.start()
			thread.append(t)
			count += 1
		for t in thread:
			t.join()
	elif region ==2:
        	for x in range(2):
			count=1
			a=serverlist[x]
			b=range(1,regionnum[regionname[x]]+1)
			for ip,num in zip(a,b):
                        	t=copyOnlineConfig(x,regionnum,regionname,count,ip,num)
                        	t.start()
                        	thread.append(t)
                        	count += 1
                	for t in thread:
                        	t.join()
		
elif checkcopyconfig == 'n' or checkcopyconfig == 'N' or checkcopyconfig == '':
	pass
else:
	print 'Wrong paramet'

checkdeploy=raw_input('Start install and deploy ? (y/N): ')
if checkdeploy == 'y' or checkdeploy == 'Y':
	pass
elif checkdeploy == 'n' or checkdeploy == 'N' or checkdeploy == '':
	sys.exit()
else:
	print 'Wrong paramet'


#Server install and deploy
subprocess.call('rm -rf /opt/awsOnline/updatelog/*',shell=True)
if region == 0 or region == 1:
	thread = []
	count=1
	while count <= regionnum[regionname[region]]:
		t=deployServer(region,regionname,count,lock)
		t.start()
		thread.append(t)
		count += 1
	for t in thread:
		t.join()
elif region == 2:
	for x in range(2):
		thread = []
		count = 1 
		while count <= regionnum[regionname[x]]:
			t=deployServer(x,regionname,count,lock)
			t.start()
			thread.append(t)
			count += 1
	for t in thread:
		t.join()
time.sleep(2)
print 'Server status'
subprocess.call('cat /opt/awsOnline/updatelog/*.log |grep Connecting',shell=True)
print ''

#MD5
checkMD5=raw_input('Enter to start MD5 compare: ')

if region == 0 or region == 1:
	thead = []
	count = 1
#	while count <= regionnum[regionname[region]]:
	for ip in serverlist[region]:
		t=md5Upload(ip,md5file,regionname,region,count,lock)
		t.start()
		checkmd5=raw_input('')
		thread.append(t)
		count += 1
	for t in thread:
                t.join()

elif region == 2:
	thread = []
	for x in range(2):
		count = 1
		for ip in serverlist[x]:
			t=md5Upload(ip,md5file,regionname,x,count,lock)
			t.start()
			checkmd5=raw_input('')
			thread.append(t)
			count += 1
	for t in thread:
                t.join()

subprocess.call('mv /root/MD5File/{0} /root/MD5File/backUP/idseagame$(date +%Y%m%d%H%M%S).md5.bak'.format(md5name),shell=True)
