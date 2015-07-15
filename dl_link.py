import mysql.connector
import codecs
db = {
    'user': 'root',
    'password': '123456',
    'database': 'ted'
}
url='http://download.ted.com/talks/%s-1500k.mp4'
cnx = mysql.connector.connect(user=db['user'], password=db['password'], database=db['database'])
cursor = cnx.cursor()
d='SELECT slug FROM ted'
cursor.execute(d)
with codecs.open('dl_link.txt','w','utf-8') as f:
	for item in cursor:
		f.write(url%item+'\n')
cursor.close()
cnx.close()
print('done')