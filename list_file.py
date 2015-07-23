import os
import codecs
path='H:/TED'
os.chdir(path)
file_list={}
for item in os.listdir('./'):
	if os.path.isdir(item):
		file_list[int(item.split('_')[0])]=item
with codecs.open('目录.txt','w','utf-8') as f:
	for key in sorted(file_list.keys()):
		f.write('├─'+file_list[key]+'\r\n')
		for file in os.listdir(file_list[key]):
			f.write('|    ├─'+file+'\r\n')
print('done')