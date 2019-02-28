#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
# Project information at https://wiki.thegpm.org/wiki/Jsms
#

import sys
import json
import re
import hashlib
import gzip

ifile = None
isGz = 0
try:
	fpath = sys.argv[1]
	if fpath.find('.gz') == -1 or fpath.rfind('.gz') != len(fpath) - 3:
		ifile = open(fpath,'r', encoding='utf-8')
	else:
		ifile = gzip.open(fpath,'rt')
		
except:
	print('Error opening file specified on command line:\ne.g. ">jsms_validator.py FILE_PATH"')
	exit()

mhash = hashlib.sha256()
ln = 1
hash = ''
es = 0
ws = 0
types = {}
for line in ifile:
	line = line.strip()
	estr = ''
	try:
		estr = 'json loading'
		js = json.loads(line)
		if 'validation' not in js:
			mhash.update(line.encode())
		else:
			estr = 'no file hash value found'
			hash = js['value']
			if 'validation' in types:
				types['validation'] += 1
			else:
				types['validation'] = 1
		if 'lv' in js:
			if 'lv' in types:
				types['lv'] += 1
			else:
				types['lv'] = 1
			estr = 'no pm key found'
			mp = js['pm']
			estr = 'no np key found'
			np = js['np']
			estr = 'no ms key found'
			if np != len(js['ms']):
				ws += 1
				print('Warning: np [%i] does not match length of array ms [%i]' % (js['np'],len(js['ms'])))
				print('line %i = %s' % (ln,line))
			estr = 'no is key found'
			if np != len(js['is']):
				ws += 1
				print('Warning: np [%i] does not match length of array is [%i]' % (js['np'],len(js['is'])))
				print('line %i = %s' % (ln,line))
		if 'format' in js:
			if 'format' in types:
				types['format'] += 1
			else:
				types['format'] = 1
			if js['format'] != 'jsms 1.0':
				es += 1
				print('Error: line %i %s' % (ln,'unsupported format "%s"' % js['format']))
				print('line %i = %s' % (ln,line))
			
	except:
		es += 1
		print('Error: line %i %s' % (ln,estr))
		print('line %i = %s' % (ln,line))
	ln += 1
if hash != mhash.hexdigest():
	print('Error: file hash does not match calculated hash\n%s - file hash\n%s - calculated' % (hash,mhash.hexdigest()))
	es += 1
if len(types) != 3:
	if 'validation' not in types:
		print('Error: file does not contain a validation object')
		es += 1
	if 'lv' not in types:
		print('Error: file does not contain an lv object')
		es += 1
	if 'format' not in types:
		print('Error: file does not contain a format object')
		es += 1
for t in types:
	print('"%s" objects = %i' % (t,types[t]))
print('Errors = %i, warnings = %i' % (es,ws))
