import json
import sys
def jsms_parse(_in):
	sp = []
	f = open(_in,'r')
	for l in f:
		o = json.loads(l)
		if 'lv' in o:
			sp.append(o)
	f.close()
	return sp

ss = jsms_parse(sys.argv[1])
for s in ss:
	print(s['pm'])
