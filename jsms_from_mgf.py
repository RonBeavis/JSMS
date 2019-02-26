#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
# Project information at https://wiki.thegpm.org/wiki/Jsms
#

import sys
import json
import re
import hashlib
import datetime
import gzip

isGz = 0

try:
	fpath = sys.argv[1]
	ifile = open(fpath,'r')
	opath = sys.argv[2]
	ofile = None
	if opath.find('.gz') == -1 or opath.rfind('.gz') != len(opath) - 3:
		print('Creating jsms plain text file ... ')
		ofile = open(opath,'w', encoding='utf-8')
	else:
		print('Creating jsms gzip file ... ')
		ofile = gzip.open(opath,'wb')
		isGz = 1
except:
	print('Error opening file specified on command line:\ne.g. ">mgf_to_jsms.py INPUT_FILE OUTPUT_FILE"')
	exit()
js = {}
Ms = []
Is = []
Zs = []
amIn = 0
mhash = hashlib.sha256()
info = {'format':'jsms 1.0','source':fpath,'created':str(datetime.datetime.now())}
str = json.dumps(info) + '\n'
if isGz == 0:
	ofile.write(str)
else:
	ofile.write(str.encode())
mhash.update(str.strip().encode())
s = 0
for line in ifile:
	line = line.rstrip()
	if line.find('BEGIN IONS') == 0:
		js = {}
		Ms = []
		Is = []
		js['lv'] = 2
		amIn = 1
	elif amIn == 0:
		continue
	elif line.find('END IONS') == 0:
		js['np'] = len(Ms)
		if len(Ms) > 0:
			js['ms'] = Ms
		if len(Is) > 0:
			js['is'] = Is
		if len(Zs) > 0:
			js['zs'] = Zs
		str = json.dumps(js)
		str += '\n'
		if isGz == 0:
			ofile.write(str)
		else:
			ofile.write(str.encode())
		mhash.update(str.strip().encode())
		amIn = 0
		s += 1
		if s % 1000 == 0:
			print('.',end='',flush=True)
		if s % 10000 == 0:
			print(' %i' % (s),flush=True)
	elif line.find('PEPMASS') == 0:
		line = re.sub('^PEPMASS\=','',line)
		js['pm'] = float(line)
	elif line.find('CHARGE=') == 0:
		line = re.sub('^CHARGE\=','',line)
		if line.find('+'):
			line = line.replace('+','')
			js['pz'] = int(line)
		else:
			line = line.replace('-','')
			js['pz'] = -1*int(line)
	elif line.find('TITLE=') == 0:
		line = re.sub('^TITLE=','',line)
		line = re.sub('\"','\'',line)
		js['ti'] = line
		if line.find('scan=') != -1:
			js['sc'] = int(re.sub('.+scan\=','',line))
		else:
			js['sc'] = s+1
	else:
		vs = line.split(' ')
		if len(vs) < 2 or len(vs) > 3:
			continue
		z = 0
		try:
			m = float(vs[0])
			if m <= 0:
				continue
			i = float(vs[1])
			if i <= 0:
				continue
			if len(vs) == 3:
				z = int(vs[2])
					
		except:
			continue
		Ms.append(m)
		Is.append(i)
		if z != 0:
			Zs.append(z)
if amIn ==1:
	print('\n\nError in file: unmatched START IONS statement')
print('\n\nspectra = %s' % (s))
info = {"validation" : "sha256", "value" : mhash.hexdigest()}
str = json.dumps(info) + '\n'
if isGz == 0:
	ofile.write(str)
else:
	ofile.write(str.encode())
print('sha256 = %s' % (mhash.hexdigest()))
ofile.close()
ifile.close()
