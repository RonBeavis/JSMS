import json
import sys
d = []
f = open(sys.argv[1],'r')
for l in f:
	o = json.loads(l)
	if 'lv' in o:
		d.append(o)
f.close()
