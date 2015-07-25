import json
import codecs
import urllib.request
import mysql.connector
import threading
db = {
    'user': 'root',
    'password': '123456',
    'database': 'ted1'
}
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36',
    'Host': 'ted2srt.org',
}


class BaseClass():

    def __init__(self):
        self.opener = None
        self.get_cnx()

    def write_utf8(self, file_dir, content):
        with codecs.open(file_dir, 'w', 'utf-8') as f:
            f.write(content)

    def read_utf8(self, file_dir):
        with codecs.open(file_dir, 'r', 'utf-8') as f:
            return f.read()

    def build_opener(self):
        self.opener = urllib.request.build_opener()
        return self.opener

    def get_html(self, url):
        if self.opener == None:
            self.build_opener()
        get = urllib.request.Request(url, headers=headers, method='GET')
        return self.opener.open(get).read().decode('utf-8')

    def json_load(self, content):
        return json.loads(content)

    def json_dump(self, content):
        return json.dumps(content, ensure_ascii=False, sort_keys=True)

    def get_cnx(self):
        self.cnx = mysql.connector.connect(
            user=db['user'], password=db['password'], database=db['database'])
        self.cursor = self.cnx.cursor()
        return self.cnx

    def get_cursor(self):
        return self.cnx.cursor()

    def multi_thread(self, num, target):  # 多线程模板
        threads = []
        for i in range(num):
            d = threading.Thread(target=target)
            threads.append(d)
        for d in threads:
            d.start()
        for d in threads:
            d.join()
if __name__ == '__main__':
    b = BaseClass()
    print(b.get_html('http://www.baidu.com'))
