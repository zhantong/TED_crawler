"""
    用来爬取TED.com中全部的TED视频，找到视频的名字、链接、时长、类别等信息，用来与ted2str配合。
"""
import urllib.request
import re
import queue
import mysql.connector
import threading
q = queue.Queue()  # 存储页数
r = {  # 需要用到的正则表达式
    'page': re.compile(r'<a class="pagination__item pagination__link" href="/talks/quick-list\?page=\d+">(\d+)</a>'),
    'div': re.compile(r"(<div class='row quick-list__row'>.*?</div>.</div>.</div>)", re.S),
    'date': re.compile(r"<spam class='meta'>\n(.*?)\n</spam>"),
    'name': re.compile(r'<span class=\'l3\'>\n<a href="(.*?)">(.*?)</a>'),
    'event': re.compile(r'<div class=\'col-xs-2 event\'>\n<span>\n<a href=".*?">(.*?)</a>'),
    'time': re.compile(r'<span class=\'meta\'></span>\n(.*?)\n</div>')
}
list_url = 'http://www.ted.com/talks/quick-list'  # 获得所有信息的页面
month = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}


def trans_date(origin):  # 将日期转换为容易索引的形式
    t = origin.split()
    return t[1] + month[t[0]]


def trans_time(origin):  # 将时长统一为秒
    if origin.find(':') != -1:
        t = origin.split(':')
        return int(t[0]) * 60 + int(t[1])
    else:
        t = origin.split()
        return int(t[0][:-1]) * 60 * 60 + int(t[1][:-1]) * 60


def init():  # 初始化工作
    con = urllib.request.urlopen(list_url)  # 首先获取网页数
    html = con.read().decode('utf-8')
    page = r['page'].findall(html)[-1]
    page = int(page)
    for i in range(1, page + 1):
        q.put(str(i))
    cnx = mysql.connector.connect(
        user='root', password='12325963', database='ted')
    cursor = cnx.cursor()
    d = ("CREATE TABLE IF NOT EXISTS ted ("  # 创建表
         "date VARCHAR(10) NOT NULL,"
         "url VARCHAR(100) NOT NULL PRIMARY KEY,"
         "name VARCHAR(100) NOT NULL,"
         "event VARCHAR(20) NOT NULL,"
         "time INT(8) NOT NULL)")
    cursor.execute(d)
    cnx.commit()
    cursor.close()
    cnx.close()


def getting():  # 爬取全部TED信息
    cnx = mysql.connector.connect(
        user='root', password='12325963', database='ted')
    cursor = cnx.cursor()
    d = ("INSERT IGNORE INTO ted "  # 数据库插入语句模板
         "(date,url,name,event,time) "
         "VALUES (%s,%s,%s,%s,%i)")
    while not q.empty():  # 便于多线程并发
        page = q.get()
        con = urllib.request.urlopen(
            list_url + '?page=' + page).read().decode('utf-8')
        for ls in r['div'].findall(con):
            date = trans_date(r['date'].findall(ls)[0])
            url = r['name'].findall(ls)[0][0]
            name = r['name'].findall(ls)[0][1]
            event = r['event'].findall(ls)[0]
            time = trans_time(r['time'].findall(ls)[0])
            d = "INSERT IGNORE INTO ted (date,url,name,event,time) VALUES ('%s','%s','%s','%s','%i')" % (
                date, url, name, event, time)
            cursor.execute(d)
        print('第%s页完成' % page)
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
    multi_thread(10, getting)
