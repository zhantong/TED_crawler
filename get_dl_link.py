import urllib.request
import mysql.connector
import queue
q=queue.Queue()
url='http://ted2srt.org'
headers={
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
}
def init():
	cnx = mysql.connector.connect(user='root', password='12325963', database='ted')
	cursor = cnx.cursor()
	d='SELECT url FROM ted'
	cursor.execute(d)
	for item in cursor:
		q.put(item[0])
	cursor.close()
	cnx.close()

def getting():
	opener=urllib.request.build_opener()
	while not q.empty():
		path=q.get()
		get=urllib.request.Request(headers=headers,url=url+path,method='GET')
		con=opener.open(get).read().decode('utf-8')
		print(con)
if __name__=='__main__':
	init()
	getting()