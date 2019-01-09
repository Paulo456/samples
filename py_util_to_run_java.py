#! /usr/bin/env python

from datetime import datetime
import subprocess, os

# type name of folder in variable date_mask or make it idle ''
date_mask = r''  # r'' # 20180702
util_name = 'smbp-ppd-migration-0.0.0.29.jar'
main_command = 'date && time sudo java -jar ' + util_name + ' '

main_path = os.getcwd() # r'/backup/migration'
path = os.path.join(main_path, date_mask)

if not date_mask:
    date_mask = datetime.now().strftime("%Y%m%d")
    path = os.path.join(main_path, date_mask)

files = [(sum(1 for line in open(i)) - 1, i) for i in [os.path.join(path, j) for j in os.listdir(path)] ]
files.sort()

commands = [('count ' + str(i), main_command + '-no-validate-service ' + j ) for (i,j) in files]
commands[0] = ('count ' + str(files[0][0]), main_command + files[0][1])

print '\n\tCommands will be executed by follow list:\n'
for i, command in enumerate(commands,1):
    print str(i)+')', command[0] + ' - ', command[1]

# process = subprocess.Popen('sudo cat /backup/migration/logs/ppdmigration-error.log', shell=True)
# print datetime.now(), "after call"

raw_input('start first one? hit ENTER, else CTRL+C - to exit ')
# print commands[0][1]
print datetime.now(), '- Running ', commands[0][1]
process = subprocess.Popen(commands[0][1], shell=True)
process.wait()

raw_input('All right? Just hit ENTER to continue ')
for command in commands:
    if command != commands[0]:
        # print command[1]
        print datetime.now(), '- Running ', command[1]
        process = subprocess.Popen(command[1], shell=True)
        process.wait()

raw_input('SUCCESS. Hit ENTER to EXIT')

