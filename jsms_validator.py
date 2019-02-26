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
	try:
		js = json.loads(line)
		if 'validation' not in js:
			mhash.update(line.encode())
		else:
			hash = js['value']
			types['validation'] = 1
		if 'lv' in js:
			types['lv'] = 1
			if js['np'] != len(js['ms']):
				ws += 1
				print('Warning: np [%i] does not match length of array ms [%i]' % (js['np'],len(js['ms'])))
			if js['np'] != len(js['is']):
				ws += 1
				print('Warning: np [%i] does not match length of array is [%i]' % (js['np'],len(js['is'])))
		if 'format' in js:
			types['format'] = 1
			
	except:
		es += 1
		print('Error: line %i not a valid JSON object' % (ln))
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

print('Errors = %i, warnings = %i' % (es,ws))
