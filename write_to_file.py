import mysql.connector
import re
import os
import codecs
import queue
import threading
import urllib.request
path="E:/TED"
os.chdir(path)
ls=[]
u='http://www.ted.com/talks/'
db = {
    'user': 'root',
    'password': '123456',
    'database': 'ted'
}
def init():
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
def write_to_file():
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
def multi_thread(num, target):  # 多线程模板
    threads = []
    for i in range(num):
        d = threading.Thread(target=target)
        threads.append(d)
    for d in threads:
        d.start()
    for d in threads:
        d.join()
def dl_photo():
	def dl():
		opener=urllib.request.build_opener()
		while not photo_q.empty():
			p=photo_q.get()
			if not os.path.exists(floder_name(p)+'/'+p['slug']+'.'+p['url'].split('.')[-1]):
				get=urllib.request.Request(url=p['url'],method='GET')
				photo=opener.open(get).read()
				with open(floder_name(p)+'/'+p['slug']+'.'+p['url'].split('.')[-1],'wb') as f:
					f.write(photo)
	photo_q=queue.Queue()
	cnx = mysql.connector.connect(
	    user=db['user'], password=db['password'], database=db['database'])
	cursor = cnx.cursor()
	query="SELECT id,name,photo_url,media_slug FROM ted"
	cursor.execute(query)
	for (id,name,photo_url,media_slug) in cursor:
		d={
		'id':str(id),
		'name':name,
		'url':photo_url,
		'slug':media_slug,
		}
		photo_q.put(d)
	cursor.close()
	cnx.close()
	multi_thread(20, dl)
def dl_subtitle(lan):
	url='http://ted2srt.org/api/talks/%s/transcripts/download/srt?lang=%s'
	def dl():
		opener=urllib.request.build_opener()
		while not subtitle_q.empty():
			p=subtitle_q.get()
			if not os.path.exists(floder_name(p)+'/'+p['slug']+'.srt'):
				get=urllib.request.Request(url=url%(p['id'],lan),method='GET')
				try:
					subtitle=opener.open(get).read()
				except Exception as e:
					print(e)
					subtitle_q.put(p)
					continue
				with open(floder_name(p)+'/'+p['slug']+'.srt','wb') as f:
					f.write(subtitle)
	subtitle_q=queue.Queue()
	cnx = mysql.connector.connect(
	    user=db['user'], password=db['password'], database=db['database'])
	cursor = cnx.cursor()
	query="SELECT id,name,media_slug FROM ted WHERE has_subtitle_%s=1"%lan
	cursor.execute(query)
	for (id,name,media_slug) in cursor:
		d={
		'id':str(id),
		'name':name,
		'slug':media_slug,
		}
		subtitle_q.put(d)
	cursor.close()
	cnx.close()
	multi_thread(3, dl)
def dl_zh_cn_subtitle():
	url='http://ted2srt.org/api/talks/%s/transcripts/download/srt?lang=%s'
	def dl():
		opener=urllib.request.build_opener()
		while not subtitle_q.empty():
			p=subtitle_q.get()
			if not os.path.exists(floder_name(p)+'/'+p['slug']+'.chs.srt'):
				get=urllib.request.Request(url=url%(p['id'],'zh-cn'),method='GET')
				try:
					subtitle=opener.open(get).read()
				except Exception as e:
					print(e)
					subtitle_q.put(p)
					continue
				with open(floder_name(p)+'/'+p['slug']+'.chs.srt','wb') as f:
					f.write(subtitle)
	subtitle_q=queue.Queue()
	cnx = mysql.connector.connect(
	    user=db['user'], password=db['password'], database=db['database'])
	cursor = cnx.cursor()
	query="SELECT id,name,media_slug FROM ted WHERE has_subtitle_%s=1"%'zh_cn'
	cursor.execute(query)
	for (id,name,media_slug) in cursor:
		d={
		'id':str(id),
		'name':name,
		'slug':media_slug,
		}
		subtitle_q.put(d)
	cursor.close()
	cnx.close()
	multi_thread(4, dl)
if __name__=='__main__':
	dl_zh_cn_subtitle()