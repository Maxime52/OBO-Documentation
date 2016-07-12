#Author: Michal Vydareny michal.vydareny@gmail.com
#
#This script imports servers(instances) to Amazon Web Service from a csv file attached as a parameter to cript call
#The expected csv file should have this form:
#
#
#The script will call AWS API via AWSCLI and will create the instances as  defined in the list, obtain the InstanceId which is returned after successfull instance creation and will use it in following call setting the tag Name
#
#The sript is called with one argument
#Argument1: the name of the csv file


import csv
import sys
import json
from os import remove,rename
from subprocess import Popen,PIPE

def returnGroupId(GroupName):
	print("I was called")
	with open('import_security_groups.csv','rb') as f:
		reader = csv.DictReader(f, delimiter=',')
		for roww in reader:
			if roww['SgName'] == GroupName:
				return roww['SgGroupId']

csv_file = sys.argv[1] 					#the csv file name
#new_csv_file = "new_file.csv"				#temporary file

#newcsvfile = open(new_csv_file,'wb')			#open temp file for writing
csvfile = open(csv_file, 'rb+')				#open csv file for reading

rulesreader = csv.DictReader(csvfile)			#access csv file
#ruleswriter = csv.writer(newcsvfile,dialect='excel')	#open temp file for csv writing

#first_row = ['SgDescription','SgName','SgGroupId']	#define first line of temp file
#ruleswriter.writerow(first_row)				#write the first line to temp file

for row in rulesreader:					#read the csv file line by line
#	print(row['IntfSecurityGroupId1'])
#	print(row['IntfSecurityGroupId2'])
	GroupId1 = str(returnGroupId(row['IntfSecurityGroupId1']))
	GroupId2 = str(returnGroupId(row['IntfSecurityGroupId2']))
#	print(GroupId1)
#	print(GroupId2)
	output,error=Popen(['aws','ec2','run-instances','--image-id',row['AWSAmiId'],'--instance-type',row['InstanceType'],'--key-name',row['KeyPairName'],'--output','json','--network-interfaces','DeviceIndex=0,SubnetId='+str(row['AWSSubnetId1'])+',PrivateIpAddress='+str(row['PrivateIpAddress1'])+',Groups='+GroupId1,'DeviceIndex=1,SubnetId='+str(row['IntfSubnetId2'])+',PrivateIpAddress='+str(row['PrivateIpAddress2'])+',Groups='+GroupId2,'--block-device-mappings','DeviceName=/dev/sdf,Ebs={VolumeSize='+str(row['StorageSize'])+'}'],stdin=PIPE,stdout=PIPE,stderr=PIPE).communicate()
	print(output)
	print(error)
	print("Naming the instance")

	json_data=json.loads(output)		#obtain the json data in output variable
	instanceId=json_data['InstanceId']	#write the GroupId json data value to row
	output,error=Popen(['aws','ec2','create-tags','--resources',instanceId,'--tags','Key=Name,Value='+row['Server']],stdin=PIPE,stdout=PIPE,stderr=PIPE).communicate()
	print(error)				#if error, show it to us. Here the script terminates in case of exception. It is odd, but no need to handle it more nicely
	print(output)

csvfile.close()						#close csv file
#newcsvfile.close()					#close temp file
#remove(csv_file)					#delete csv file from system
#rename(new_csv_file,csv_file)				#rename temp file to csv file name
