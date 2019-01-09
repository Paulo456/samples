#! /usr/bin/env python

path_file1 = r'/backup/customer-status-provider/activePersonAccountsForForis_111_29_05_2018.csv'
path_file2 = r'/backup/customer-status-provider/arcdump/activePersonAccountsForForis_111_29_05_2018.csv'
path_file3 = r'/backup/customer-status-provider/diffrence_29.05.2018_MRM.csv'

nabor1 = set([ (x.strip('\n').split(';')[0], x.strip('\n').split(';')[2]) for x in open(path_file1, 'r')])
nabor2 = set([ (x.strip('\n').split(';')[0], x.strip('\n').split(';')[2]) for x in open(path_file2, 'r')])

nabor = nabor1 - nabor2
msisdns = []

for i in nabor:
    msisdns.append(i[0])

nabor3 = [x.strip('\n') for x in open(path_file2, 'r')]
print(len(nabor))

text = ''

for j in nabor3:
    if j.split(';')[0] in msisdns:
        text += str(j) + '\n'

f4 = open(path_file3, 'w')
f4.write(text)
f4.close()
