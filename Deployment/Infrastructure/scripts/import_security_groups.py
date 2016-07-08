#Author: Michal Vydareny michal.vydareny@gmail.com
#
#This script imports security group for Amazon Web Service from a csv file attached as a parameter to cript call
#The expected csv file should have this form:
#
#SgDescription,SgName,SgGroupId
#some description1,name1,
#some description2,name2,
#
#The script will call AWS API via AWSCLI and will create the security groups defined in the list, obtain the GroupId which is returned after successfull Group creation
#The SgGroupId column will be filled up with the returned values and the file can be then used as an input for next script which will deploy the whole infrastructure
#
#The sript is called with two arguments
#Argument1: the name of the csv file
#Argument2: the VPC ID from AWS


import csv
import sys
import json
from os import remove,rename
from subprocess import Popen,PIPE

csv_file = sys.argv[1] 					#the csv file name
vpc_id = sys.argv[2]					#the VPC ID
new_csv_file = "new_file.csv"				#temporary file

newcsvfile = open(new_csv_file,'wb')			#open temp file for writing
csvfile = open(csv_file, 'rb+')				#open csv file for reading

rulesreader = csv.DictReader(csvfile)			#access csv file
ruleswriter = csv.writer(newcsvfile,dialect='excel')	#open temp file for csv writing

first_row = ['SgDescription','SgName','SgGroupId']	#define first line of temp file
ruleswriter.writerow(first_row)				#write the first line to temp file

for row in rulesreader:					#read the csv file line by line
	print(row)
	output,error=Popen(['aws','ec2','create-security-group','--group-name',row['SgName'],'--description',row['SgDescription'],'--vpc-id',vpc_id,'--output','json'],stdin=PIPE,stdout=PIPE,stderr=PIPE).communicate()	#call awscli with parameters
	print("aaa")
	try:
		json_data=json.loads(output)		#obtain the json data in output variable
		row['SgGroupId']=json_data['GroupId']	#write the GroupId json data value to row
		ruleswriter.writerow(row.values())	#write the whole row to temp file
	except:
		print(error)				#if error, show it to us. Here the script terminates in case of exception. It is odd, but no need to handle it more nicely

csvfile.close()						#close csv file
newcsvfile.close()					#close temp file
#remove(csv_file)					#delete csv file from system
#rename(new_csv_file,csv_file)				#rename temp file to csv file name
