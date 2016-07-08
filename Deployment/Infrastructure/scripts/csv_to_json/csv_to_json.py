# Author: Michal Vydareny michal.vydareny@gmail.com
#
# The script takes csv files as input and translates them to JSON file suitable for Amazon CloudFormation
#
# The name of the file must be in a form of resource type in AM, where the colon is replaced by underscore:
# input file name: AWS_EC2_Subnet.csv -> script makes it an AWS resource AWS::EC2::Subnet
#
# Name of columns in the csv file represents the hierarchy of the AWS Json file.
# E.g.: SourceSecurityGroupName/Ref results to:
# "SourceSecurityGroupName": {
#    "Ref":"value"
# }
#
# Some of the hierarchy levels require to be type: list. In such a case, the number in the hierarchy forces type list and the number represents the position in the list.
# E.g.: BlockDeviceMappings/0/DeviceName results to:
#
# "BlockDeviceMappings": [
#    {
#       "DeviceName": "value"
#    }
# ]
#
#
# or NetworkInterfaces/1/GroupSet/1/Ref results to:
#
# "NetworkInterfaces": [
#    {
#       "GroupSet": [
#          {
#             "Ref":"value"
#          }
#       ]
#    }
# ]
#
#
# The logical dependency is not verified by the script. CloudFormation will perform the logical check.
# However, each CSV file must contain column named Resources, which uniqely identifies each row in the CSV table and represents the AWS resource name.
# Each Column name starting with underscore is ignored by the script - servers for user comments or other helper values
#
#############################################################################################################

import csv
import sys
import json

def new(list_of_headers,json_value,json_data):								# Function expects on the input the list of headers, specific value from the particular column/row, and supporting variable json_data
	for position,header in enumerate(list_of_headers):						# iterate over the list of headers
		if (position+1)==len(list_of_headers):							# if it is the deepest position, write the json value to the json_data dict
			json_data[header]=json_value
		else:
			if header.isdigit():								# if the particular level is a number
				if len(json_data)==0 | int(header)==len(json_data):			# test whether the list on this level is empty or the same lenght and the number in the level
					json_data.append({})						# if so, add a new position to the list
					list_of_headers.pop(0)						# remove the top hierarchy level
					new(list_of_headers,json_value,json_data[int(header)])		# and call the function itself again with shorter list of headers
				else:									# if there is list on this position in json_data
					list_of_headers.pop(0)
					new(list_of_headers,json_value,json_data[int(header)])		# call the function itself with shorter list of headers to fill the position
			else:										# if the level is not a digit
				if header in json_data.keys():						# check for existence of hierarchy level with this name
					list_of_headers.pop(0)						# if there is one, call the function itself with shorter list of headers to fill in the value
					new(list_of_headers,json_value,json_data[header])
				else:									# if the level name is new to the dictionary
					if list_of_headers[position+1].isdigit():			# and there is a following numeric level name
						json_data[header]=[]					# add a list to this position
						list_of_headers.pop(0)
						new(list_of_headers,json_value,json_data[header])	# call the function itself to fill in the values
					else:								# if there is no following number in the list of headers
						json_data[header]={}					# add a dictionary to this dictionary position
						list_of_headers.pop(0)					# and call the function itself to fill in the values
						new(list_of_headers,json_value,json_data[header])
	return json_data										# return the final json_data after all the iterations and recursions.

json_file = open('aws_json.json','wb+')				#open file named aws_json.json If such a file exists in the working directory, it will be overwritten

json_content = {}						# define a variable type dictionary

for file in sys.argv[1:]:					# for each file in the list of files provided during the script call...
	csv_file = open(file,'rU')				# open the file
	rowsreader = csv.DictReader(csv_file,delimiter=',')	# read all rows to variable
	headers_list = {} 					# define a variable that will hold the list of headers
	file_name_list = file.split('.')			# split the file name and the file extension
	if file_name_list[0]=='AWS_ElasticLoadBalancing_LoadBa': file_name_list[0]='AWS_ElasticLoadBalancing_LoadBalancer'	#this is due to limited length of the excel tab names
	file_name = file_name_list[0].replace('_','::')		# in a file name replace "_" with "::"
	for n in rowsreader.fieldnames:				# iterate over list of column names
		headers_list[n] = n
		if n=="Resources": check=True			# if the is column name "Resources" set the check to True

	if check!=True: print("Missing \"Resources\" field in file: ",file)	#if there is missing "Resources" column name, let the user know and finish the script
	else:
		print("Resources header check ............ OK")			#otherwise print the check passed and continue
		for row in rowsreader:						# for each row in the list of rows
			d={}							# define a helper variable
			depends_on=''
			for header in headers_list:				# for each column name in the list of headers
				if header=='DependsOn': 
					depends_on=row['DependsOn']
					print "aa"
					print depends_on
				elif (header!='Resources')&(row['Resources']!='')&(header[0]!='_'):	#verify if the column name is not Resources, or the Resources value is not empty, or the name is not starting by underscore
					if '/' not in header:					# if the column name does not contain '/' it means there is top JSON position only, so it is written to the final JSON file
						d.update({header:row[header]})
					elif row[header]!='na':					# otherwise split the column name by '/' and store the levels to a variable
						levels_list = header.split('/')
						d=new(levels_list,row[header],d)		# call a function that will iterate through the levels and generate JSON file
			if 'Resources' in json_content:						# write/update the returned JSON value from the function to the json_content variable
				if depends_on!='':
					print "ee"
					json_content['Resources'][row['Resources']]={'Type':file_name,'Properties':d,'DependsOn':depends_on}
				else:
					json_content['Resources'][row['Resources']]={'Type':file_name,'Properties':d}
			else:
				if depends_on!='':
					print "uu"
					json_content.update({'Resources' : { row['Resources'] : {'Type':file_name,'Properties':d,'DependsOn':depends_on}}})
				else:
					json_content.update({'Resources' : { row['Resources'] : { 'Type' : file_name , 'Properties' : d }}})
json.dump(json_content,json_file)	# store the final value to json file
