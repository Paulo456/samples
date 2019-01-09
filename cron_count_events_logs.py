#! /usr/bin/env python

#25      *       *       *       *        /usr/local/src/scripts/count_events_smbp_hour.py  >> /backup/logs/cron_python_count.log 2>&1

from datetime import timedelta, datetime
import os, commands, json, re

path_date_mask_file = r'/backup/logs/temp_date_mask.txt'
path_csv_file = r'/backup/logs/count_events_smbp_hour.csv'
date_mask = (datetime.now() - timedelta(hours=1)).strftime("%Y%m%d_%H")
uptime_command = commands.getoutput('uptime')
value_list = ['01: eventTypeId=', 'Result: code=']

def session_from_string(string):
	return re.search(r'\d+', string).group(0)

def event_from_string(string, txt):
	return session_from_string(string.split(txt)[1])

if float(uptime_command.split('load average: ')[1].split(',')[0]) < 15:
	
	date_mask_list = []
	if os.path.isfile(path_date_mask_file):
		date_mask_list = [x.strip('\n') for x in open(path_date_mask_file, 'r')]
		os.remove(path_date_mask_file)
	date_mask_list.append(date_mask)

	for date_mask in date_mask_list:
		dict_list = {'Date':str(date_mask),'file_size':0,'error':{}}
		dict_events = {}
		dict_errors = {}
		files = commands.getoutput('/bin/find /opt/smbp/logs -name "*{}*"'.format(date_mask)).split('\n')

		if files[0]:
			for file in files:
				if not os.path.isfile(file):
					file = file + '.gz'
				strings = commands.getoutput('zegrep "{vl[0]}|{vl[1]}" {file} | grep -v "{vl[1]}0" '.format(vl=value_list, file=file)).split('\n')
				for string in strings:
					if value_list[0] in string:
						event = event_from_string(string, value_list[0])
						session = session_from_string(string)
						dict_events[session] = event
						if event not in dict_list:
							dict_list[event] = 0
						dict_list[event] += 1
						continue
					elif value_list[1] in string:
						error = event_from_string(string, value_list[1])
						session = session_from_string(string)
						dict_errors[session] = error
				dict_list['file_size'] += os.path.getsize(file)
				
		for session in dict_errors:
			if session in dict_events:
				new_error = str(dict_events[session]) + ': ' + str(dict_errors[session])
			else:
				new_error = 'Not found: ' + str(dict_errors[session])
			if new_error not in dict_list['error']:
				dict_list['error'][new_error] = 0
			dict_list['error'][new_error] += 1
		
		f1 = open(path_csv_file, 'a')
		f1.write(json.dumps(dict_list, sort_keys=True)+'\n')
		f1.close()
else:
	f4 = open(path_date_mask_file, 'a')
	f4.write(date_mask + '\n')
	f4.close()
