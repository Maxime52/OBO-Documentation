# Author: Michal Vydareny
# Contact: michal.vydareny@gmail.com
#
# Script takes excel file provided as script call parameter and stores it as multiple csv files. Each sheet represents one csv file. The file name is obtained from the sheet name.
#
# !!!Each single cell in excel must be type "text" otherwise the script will start to complain about encoding issues
#
#
#

import io
import openpyxl
import sys

file=sys.argv[1]		# excel file provided as parameter
wb = openpyxl.load_workbook(file,data_only=True)

line=u''

for sheet in wb.get_sheet_names():
	file_name=sheet.encode('ascii')+'.csv'
	file = io.open(file_name,'w',encoding='utf-8')
	sheet=wb.get_sheet_by_name(sheet.encode('ascii','ignore'))
	for row in sheet.rows:
		for column in row:
			value=unicode(column.value)
			if value!='None':
				if line=='': line=value
				else: line=line+','+value
		print line
		file.write(line+'\n')
		line=''
	file.close()
