import urllib.request
import urllib.error
import mysql.connector
import queue
import json
import re
import threading
q = queue.Queue()
api_url = 'http://ted2srt.org/api'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36',
    'Host': 'ted2srt.org',
}
db = {
    'user': 'root',
    'password': '123456',
    'database': 'ted'
}
chinese = {
    'name': 'Chinese, Simplified',
    'code': 'zh-cn'}
english = {
    'name': 'English',
    'code': 'en'}
update = "UPDATE ted SET has_chinese='%s',has_english='%s',name_2='%s',slug='%s',description='%s',images='%s',id='%s' WHERE url='%s'"


def init():
    cnx = mysql.connector.connect(
        user=db['user'], password=db['password'], database=db['database'])
    cursor = cnx.cursor()
#	add_field=('ALTER TABLE ted ADD has_english TINYINT(1) DEFAULT 0,'
#		'ADD has_chinese TINYINT(1) DEFAULT 0,'
#		'ADD name_2 VARCHAR(100) DEFAULT NULL,'
#		'ADD slug VARCHAR(100) DEFAULT NULL,'
#		'ADD description MEDIUMTEXT DEFAULT NULL,'
#		'ADD images VARCHAR(200) DEFAULT NULL,'
#		'ADD id VARCHAR(10) DEFAULT NULL')
    d = 'SELECT url FROM ted'
    cursor.execute(d)
    for item in cursor:
        q.put(item[0])
#	cursor.execute(add_field)
    cursor.close()
    cnx.close()

count=0
def getting():
    global count
    opener = urllib.request.build_opener()
    cnx = mysql.connector.connect(
        user=db['user'], password=db['password'], database=db['database'])
    cursor = cnx.cursor()
    while not q.empty():
        chi = '0'
        eng = '0'
        path = q.get()
        get = urllib.request.Request(
            headers=headers, url=api_url+path, method='GET')
        try:
            con = opener.open(get).read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print(e)
            if e.code=='404':
                continue
        except Exception as e:
            print(e)
            q.put(path)
            continue
        count+=1
        print(count)
        j = json.loads(con)
        if chinese in j['languages']:
            chi = '1'
        if english in j['languages']:
            eng = '1'
        cursor.execute(update % (chi, eng, re.escape(j['talk']['name']), re.escape(j['talk']['mSlug']), re.escape(
            j['talk']['description']), re.escape(j['talk']['images']['medium']), j['talk']['id'], path))
    cnx.commit()
    cursor.close()
    cnx.close()


def multi_thread(num, target):  # 多线程模板
    threads = []
    for i in range(num):
        d = threading.Thread(target=target)
        threads.append(d)
    for d in threads:
        d.start()
    for d in threads:
        d.join()
if __name__ == '__main__':
    init()
    multi_thread(3, getting)
