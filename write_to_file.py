import mysql.connector
import re
import os
import codecs
path="E:/TED"
os.chdir(path)
ls=[]
u='http://www.ted.com/talks/'
def init():
	db = {
	    'user': 'root',
	    'password': '123456',
	    'database': 'ted'
	}
	cnx = mysql.connector.connect(
	    user=db['user'], password=db['password'], database=db['database'])
	cursor = cnx.cursor()
	query="SELECT id,name,name_zh_cn,native_language_code,description,description_zh_cn,published_at,media_duration,slug,media_1500k,speaker_id,tags FROM ted"
	cursor.execute(query)
	for (id,name,name_zh_cn,native_language_code,description,description_zh_cn,published_at,media_duration,slug,media_1500k,speaker_id,tags) in cursor:
		t={
		'id':str(id),
		'name':name,
		'name_zh_cn':name_zh_cn,
		'native_language_code':native_language_code,
		'description':description,
		'description_zh_cn':description_zh_cn,
		'published_at':published_at,
		'media_duration':media_duration,
		'url':u+slug,
		'media_1500k':media_1500k,
		'mp4_name':media_1500k.split('/')[-1],
		'speaker_id':speaker_id,
		'tags':tags,
		}
		ls.append(t)
	cursor.close()
	cnx.close()
def floder_name(d):
	rstr = r"[\/\\\:\*\?\"\<\>\|\.]"
	return d['id']+'_'+re.sub(rstr, ' ', d['name']).strip()
info=("ID: %(id)s\r\n"
	"英文标题: %(name)s\r\n"
	"中文标题: %(name_zh_cn)s\r\n"
	"标签: %(tags)s\r\n"
	"语言: %(native_language_code)s\r\n"
	"时长: %(media_duration)s\r\n"
	"发布日期: %(published_at)s\r\n"
	"链接: %(url)s\r\n"
	"视频下载链接: %(media_1500k)s\r\n"
	"演讲者ID: %(speaker_id)s")
def test():
	for item in ls:
		if not os.path.exists(floder_name(item)):
			os.mkdir(floder_name(item))
		if not os.path.exists(floder_name(item)+'/info.txt'):
			with codecs.open(floder_name(item)+'/info.txt','w','utf-8') as f:
				f.write(info%item)
		if not os.path.exists(floder_name(item)+'/description.txt'):
			with codecs.open(floder_name(item)+'/description.txt','w','utf-8') as f:
				f.write(item['description'])
		if not os.path.exists(floder_name(item)+'/中文介绍.txt'):
			with codecs.open(floder_name(item)+'/中文介绍.txt','w','utf-8') as f:
				f.write(item['description_zh_cn'])
		if os.path.exists(item['mp4_name']):
			os.rename(item['mp4_name'],floder_name(item)+'/'+item['mp4_name'])
if __name__=='__main__':
	init()
	test()