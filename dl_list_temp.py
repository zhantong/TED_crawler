import mysql.connector
import os
exist = []
for root, dirs, files in os.walk("E:\TED"):
	for name in files:
		exist.append(name)
db = {
    'user': 'root',
    'password': '123456',
    'database': 'ted'
}
cnx = mysql.connector.connect(
    user=db['user'], password=db['password'], database=db['database'])
cursor = cnx.cursor()
select='SELECT media_1500k FROM ted'
cursor.execute(select)
for item in cursor:
	if item[0]!='':
		if not item[0].split('/')[-1] in exist:
			print(item[0])