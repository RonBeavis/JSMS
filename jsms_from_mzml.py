#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
# Project information at https://wiki.thegpm.org/wiki/Jsms
#

import xml.sax
import sys
import json
import struct
import base64
import hashlib
import datetime
import gzip
import zlib

class mzMLHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.cTag = ''
		self.isSpectrum = False
		self.isSelectedIon = False
		self.isMzArray = False
		self.isIntArray = False
		self.isBinaryDataArray = False
		self.isBinary = False
		self.isZlib = False
		self.jsms = {}
		self.floatBytes = 8
		self.content = ''
		self.ofile = None
		self.mhash = None
		self.isGf = 0
	
	def addFile(self,of,mh,gz):
		self.ofile = of
		self.mhash = mh
		self.isGz = gz
		
	def startElement(self, tag, attrs):
		self.cTag = tag
		if tag == 'spectrum':
			self.isSpectrum = True
		if self.isSpectrum and tag == 'cvParam':
			if attrs['name'] == 'ms level':
				self.jsms['lv'] = attrs['value']
		if tag == 'selectedIon':
			self.isSelectedIon = True
		if self.isSelectedIon and tag == 'cvParam':
			if attrs['name'] == 'selected ion m/z':
				self.jsms['pm'] = attrs['value']
			if attrs['name'] == 'charge state':
				self.jsms['pz'] = attrs['value']
		if tag == 'binaryDataArray':
			self.isBinaryDataArray = True
		if self.isBinaryDataArray and tag == 'cvParam':
			if attrs['name'] == 'm/z array':
				self.isMzArray = True
			if attrs['name'] == 'intensity array':
				self.isIntArray = True
			if attrs['name'] == '32-bit float':
				self.floatBytes = 4
			if attrs['name'] == '64-bit float':
				self.floatBytes = 8
			if attrs['name'] == 'zlib compression':
				self.isZlib = True
		if (self.isMzArray or self.isIntArray) and tag == 'binary':
			self.isBinary = True
	def characters(self, content):
		if self.isMzArray or self.isIntArray:
			self.content += content

	def endElement(self, tag):
		if tag == 'spectrum':
			self.isSpectrum = False
			if len(self.jsms) > 0:
				str = json.dumps(self.jsms)
				self.mhash.update(str.encode())
				str += '\n'
				if self.isGz == 0:
					self.ofile.write(str)
				else:
					self.ofile.write(str.encode())
			self.jsms = {}
		if tag == 'selectedIon':
			self.isSelectedIon = False
		if tag == 'binaryDataArray':
			self.isBinaryDataArray = False
		if tag == 'binary':
			self.isBinary = False
			if self.isMzArray:
				str = self.content.strip()
				if self.isZlib:
					d = base64.standard_b64decode(str.encode())
					data = zlib.decompress(d)
					count = len(data)/int(self.floatBytes)
					if self.floatBytes == 4:
						result = struct.unpack('<%if' % (count),data)
					else:
						result = struct.unpack('<%id' % (count),data)
				else:
					data = base64.standard_b64decode(str.encode())
					count = len(data)/int(self.floatBytes)
					if self.floatBytes == 4:
						result = struct.unpack('<%if' % (count),data)
					else:
						result = struct.unpack('<%id' % (count),data)
					
				self.jsms['ms'] = result
				self.jsms['np'] = len(result)
				self.isMzArray = False
				self.isZlib = False
				self.content = ''
			if self.isIntArray:
				str = self.content.strip()
				if self.isZlib:
					d = base64.standard_b64decode(str.encode())
					data = zlib.decompress(d)
					count = len(data)/int(self.floatBytes)
					if self.floatBytes == 4:
						result = struct.unpack('<%if' % (count),data)
					else:
						result = struct.unpack('<%id' % (count),data)
				else:
					data = base64.standard_b64decode(str.encode())
					count = len(data)/int(self.floatBytes)
					if self.floatBytes == 4:
						result = struct.unpack('<%if' % (count),data)
					else:
						result = struct.unpack('<%id' % (count),data)
				self.jsms['is'] = result
				self.isIntArray = False
				self.content = ''

isGz = 0
try:
	fpath = sys.argv[1]
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
	print('Error opening file specified on command line:\ne.g. ">jsms_to_mzML.py INPUT_FILE OUTPUT_FILE"')
	exit()
mhash = hashlib.sha256()
info = {'format':'jsms 1.0','source':fpath,'created':str(datetime.datetime.now())}
str = json.dumps(info) + '\n'
if isGz == 0:
	ofile.write(str)
else:
	ofile.write(str.encode())
mhash.update(str.strip().encode())
parser = xml.sax.make_parser()
parser.setContentHandler(mzMLHandler())
parser.getContentHandler().addFile(ofile,mhash,isGz)
parser.parse(open(fpath,"r"))
info = {"validation" : "sha256", "value" : mhash.hexdigest()}
str = json.dumps(info) + '\n'
if isGz == 0:
	ofile.write(str)
else:
	ofile.write(str.encode())
