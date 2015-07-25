import urllib.request
import time
import codecs
import re
import baseClass
import queue
import os

api_key = 'pykzs7satj3sabhpnh6j39p5' #需要从TED官网申请

path = "G:\TED_20150715"#TED目录


class Counter(dict):#解决KeyError问题

    def __missing__(self, key):#若key不存在，则返回空字符串
        return ''


class TED(baseClass.BaseClass):

    def __init__(self):
        self.talk_info = []
        baseClass.BaseClass.__init__(self)#需要手动触发父级__init__
        self.write_list = []
        self.video_list = []

    def dl_from_api(self):#从官网API接口获得全部视频信息
        offset = 0#API接口限制，需要分多次抓取
        url = ('http://api.ted.com/v1/talks.json?api-key=%s'
               '&limit=100'#每次获取100条
               '&offset=%i'#指定从哪条开始获取
               '&fields=photo_urls,media,media_profile_uris,speaker_ids,speakers,theme_ids,tags')#附加内容
        while 1:
            try:
                con = self.get_html(url % (api_key, offset))
            except Exception as e:
                print(e)
                continue
            j = self.json_load(con)
            for item in j['talks']:
                self.talk_info.append(item['talk'])
            print('id begin with:%i' % j['talks'][0]['talk']['id'])
            if j['counts']['this'] != 100: #最后一次获取到的条数会小于100
                break
            offset += 100#偏移每次100
            time.sleep(0.5)#API限制1秒最多2次
        self.write_utf8('ted_json', self.json_dump(self.talk_info))#将所有视频英文信息存储到json格式文件

    def get_eng_info(self):#将获得的英文视频信息存储至数据库，每次都会删除原先的数据库，建立新的数据库，这样来确保数据库中内容均为最新
        drop_table = "DROP TABLE IF EXISTS ted"
        self.cursor.execute(drop_table)#删除原数据库
        create_table = (
            "CREATE TABLE ted ("
            "id INT(6) NOT NULL PRIMARY KEY,"
            "event_id INT(6) NOT NULL,"
            "name VARCHAR(100) NOT NULL,"
            "name_zh_cn VARCHAR(200) NOT NULL,"
            "native_language_code VARCHAR(10) NOT NULL,"
            "description TEXT NOT NULL,"
            "description_zh_cn TEXT NOT NULL,"
            "recorded_at TIMESTAMP NOT NULL,"
            "updated_at TIMESTAMP NOT NULL,"
            "slug VARCHAR(100) NOT NULL,"
            "media_created_at TIMESTAMP NOT NULL,"
            "media_duration VARCHAR(20) NOT NULL,"
            "media_id INT(6) NOT NULL,"
            "media_slug VARCHAR(100) NOT NULL,"
            "media_1500k VARCHAR(100) NOT NULL,"
            "media_2500k VARCHAR(100) NOT NULL,"
            "media_480p VARCHAR(100) NOT NULL,"
            "audio VARCHAR(100) NOT NULL,"
            "photo_url VARCHAR(200) NOT NULL,"
            "speaker_id INT(6) NOT NULL,"
            "tags VARCHAR(200) NOT NULL,"
            "has_subtitle_en TINYINT(1) NOT NULL,"
            "has_subtitle_zh_cn TINYINT(1) NOT NULL)")
        self.cursor.execute(create_table)#创建新数据库
        insert = ("INSERT IGNORE INTO ted "
                  "(id,event_id,name,native_language_code,description,"
                  "recorded_at,updated_at,slug,media_created_at,media_duration,"
                  "media_id,media_slug,media_1500k,media_2500k,media_480p,audio,photo_url,"
                  "speaker_id,tags,has_subtitle_en,has_subtitle_zh_cn) "
                  "VALUES ('%(id)s','%(event_id)s','%(name)s','%(native_language_code)s',"
                  "'%(description)s','%(recorded_at)s','%(updated_at)s',"
                  "'%(slug)s','%(media_created_at)s','%(media_duration)s','%(media_id)s',"
                  "'%(media_slug)s','%(media_1500k)s','%(media_2500k)s','%(media_480p)s',"
                  "'%(audio)s','%(photo_url)s','%(speaker_id)s','%(tags)s','%(has_subtitle_en)s',"
                  "'%(has_subtitle_zh_cn)s')")
        j = self.json_load(self.read_utf8('ted_json'))#获得之前存储的内容
        for t in j:
            tags = ''
            try:
                for tag in t['tags']:#将tags list转换为string
                    tags = tags + tag + ', '
                tags = tags[:-2]
                print('inserting id %s to database' % t['id'])
                info = {
                    'id': t['id'],
                    'event_id': t['event_id'],
                    'name': re.escape(t['name']),
                    'native_language_code': t['native_language_code'],
                    'description': re.escape(t['description']),#escape()避免插入MySQL出错
                    'recorded_at': t['recorded_at'],
                    'updated_at': t['updated_at'],
                    'slug': t['slug'],
                    'photo_url': t['photo_urls'][1]['url'],
                    'speaker_id': t['speaker_ids'][0],
                    'tags': tags,
                }
                if t['media']:#以下均需首先判断key是否存在
                    info['media_created_at'] = t['media']['created_at']
                    info['media_duration'] = t['media']['duration']
                    info['media_id'] = t['media']['id']
                    info['media_slug'] = t['media']['slug']
                if 'internal' in t['media_profile_uris']:
                    if 'podcast-high-en' in t['media_profile_uris']['internal']:
                        info['has_subtitle_en'] = 1
                    else:
                        info['has_subtitle_en'] = 0
                    if 'podcast-high-zh-cn' in t['media_profile_uris']['internal']:
                        info['has_subtitle_zh_cn'] = 1
                    else:
                        info['has_subtitle_zh_cn'] = 0
                    if '1500k' in t['media_profile_uris']['internal']:
                        info['media_1500k'] = t['media_profile_uris'][
                            'internal']['1500k']['uri']
                    if '2500k' in t['media_profile_uris']['internal']:
                        info['media_2500k'] = t['media_profile_uris'][
                            'internal']['2500k']['uri']
                    if 'podcast-high' in t['media_profile_uris']['internal']:
                        info['media_480p'] = t['media_profile_uris'][
                            'internal']['podcast-high']['uri']
                    if 'audio-podcast' in t['media_profile_uris']['internal']:
                        info['audio'] = t['media_profile_uris'][
                            'internal']['audio-podcast']['uri']
                info = Counter(info)#避免KeyError，但不能完全避免
            except KeyError as e:
                print('key error:', e)
            self.cursor.execute(insert % info)#将演讲英文信息插入到数据库
        self.cnx.commit()

    def get_chi_info(self): #从TED官网获取视频中文信息，因为部分视频不存在中文信息，所以先抓取英文再抓取中文
        offset = 0#API接口限制，需要分多次抓取
        url = ('http://api.ted.com/v1/talks.json?api-key=%s'
               '&limit=100'
               '&offset=%i'
               '&language=zh-cn')#指定语言
        update = (
            "UPDATE ted SET name_zh_cn='%s',description_zh_cn='%s' WHERE id='%s'")
        while 1:
            try:
                con = self.get_html(url % (api_key, offset))
            except Exception as e:
                print(e)
                continue
            j = self.json_load(con)
            for item in j['talks']:
                self.cursor.execute(update % (re.escape(item['talk']['name']), re.escape(
                    item['talk']['description']), item['talk']['id']))
                print('updated id %i' % item['talk']['id'])
            if j['counts']['this'] != 100:
                break
            offset += 100
            time.sleep(0.5)
        self.cnx.commit()

    def list_file(self):#生成目录树
        os.chdir(path)#修改当前路径为TED文件夹
        file_list = {}
        for item in os.listdir('./'):
            if os.path.isdir(item):
                file_list[int(item.split('_')[0])] = item
        with codecs.open('目录.txt', 'w', 'utf-8') as f:
            for key in sorted(file_list.keys()):
                f.write('├─' + file_list[key] + '\r\n')
                for file in os.listdir(file_list[key]):
                    f.write('|    ├─' + file + '\r\n')
        print('done')

    def floder_name(self, d):#从视频ID和name生成文件夹名
        rstr = r"[\/\\\:\*\?\"\<\>\|\.]"#去除不能用于文件夹名的符号
        return d['id'] + '_' + re.sub(rstr, ' ', d['name']).strip()

    def write_to_file(self):#将info、中文介绍、英文介绍写入到文件，并且移动视频到相应文件夹
        os.chdir(path)#修改当前目录到TED文件夹
        u = 'http://www.ted.com/talks/'#用于生成此演讲URL
        query = "SELECT id,name,name_zh_cn,native_language_code,description,description_zh_cn,recorded_at,media_duration,slug,media_1500k,speaker_id,tags FROM ted"
        self.cursor.execute(query)
        for (id, name, name_zh_cn, native_language_code, description, description_zh_cn, recorded_at, media_duration, slug, media_1500k, speaker_id, tags) in self.cursor:
            t = {
                'id': str(id),
                'name': name,
                'name_zh_cn': name_zh_cn,
                'native_language_code': native_language_code,
                'description': description,
                'description_zh_cn': description_zh_cn,
                'recorded_at': recorded_at,
                'media_duration': media_duration,
                'url': u + slug,
                'media_1500k': media_1500k,
                'mp4_name': media_1500k.split('/')[-1],
                'speaker_id': speaker_id,
                'tags': tags,
            }
            self.write_list.append(t)
        info = ("ID: %(id)s\r\n"
                "英文标题: %(name)s\r\n"
                "中文标题: %(name_zh_cn)s\r\n"
                "标签: %(tags)s\r\n"
                "语言: %(native_language_code)s\r\n"
                "时长: %(media_duration)s\r\n"
                "日期: %(recorded_at)s\r\n"
                "链接: %(url)s\r\n"
                "视频下载链接: %(media_1500k)s\r\n"
                "演讲者ID: %(speaker_id)s")
        for item in self.write_list:
            floder_name = self.floder_name(item)
            if not os.path.exists(floder_name):#若文件夹不存在则创建
                os.mkdir(floder_name)
            if not os.path.exists(floder_name + '/info.txt'):#info
                self.write_utf8(floder_name + '/info.txt', info % item)
            if not os.path.exists(floder_name + '/description.txt'):#英文介绍
                self.write_utf8(
                    floder_name + '/description.txt', item['description'])
            if not os.path.exists(floder_name + '/中文介绍.txt'):#中文介绍
                self.write_utf8(
                    floder_name + '/中文介绍.txt', item['description_zh_cn'])
            if os.path.exists(item['mp4_name']):#将视频移动到相应文件夹
                os.rename(
                    item['mp4_name'], floder_name + '/' + item['mp4_name'])

    def dl_photo(self):#下载演讲照片
        def dl():#多线程处理
            opener = urllib.request.build_opener()
            while not photo_q.empty():
                p = photo_q.get()
                file_name = self.floder_name(
                    p) + '/' + p['slug'] + '.' + p['url'].split('.')[-1]
                if not os.path.exists(file_name):#如果照片不存在，则下载
                    get = urllib.request.Request(url=p['url'], method='GET')
                    photo = opener.open(get).read()
                    with open(file_name, 'wb') as f:
                        f.write(photo)
        photo_q = queue.Queue()
        query = "SELECT id,name,photo_url,media_slug FROM ted"
        self.cursor.execute(query)
        for (id, name, photo_url, media_slug) in self.cursor:
            d = {
                'id': str(id),
                'name': name,
                'url': photo_url,
                'slug': media_slug,
            }
            photo_q.put(d)
        self.multi_thread(20, dl)

    def dl_subtitle(self, lan):#下载字幕，参数为cn或zh-cn
        language = {
            'en': {'db': 'en',
                   'srt': 'en'},
            'zh-cn': {'db': 'zh_cn',
                      'srt': 'chs'}
        }
        url = 'http://ted2srt.org/api/talks/%s/transcripts/download/srt?lang=%s'#从ted2srt下载字幕

        def dl():#多线程处理
            opener = urllib.request.build_opener()
            while not subtitle_q.empty():
                p = subtitle_q.get()
                file_name = self.floder_name(
                    p) + '/' + p['slug'] + '.' + language[lan]['srt'] + '.srt'
                if not os.path.exists(file_name):#如果字幕不存在则下载
                    get = urllib.request.Request(
                        url=url % (p['id'], lan), method='GET')
                    try:
                        subtitle = opener.open(get).read()
                    except Exception as e:
                        print(e)
                        subtitle_q.put(p)
                        continue
                    with open(file_name, 'wb') as f:
                        f.write(subtitle)
        subtitle_q = queue.Queue()
        query = "SELECT id,name,media_slug FROM ted WHERE has_subtitle_%s=1" % language[
            lan]['db']
        self.cursor.execute(query)
        for (id, name, media_slug) in self.cursor:
            d = {
                'id': str(id),
                'name': name,
                'slug': media_slug,
            }
            subtitle_q.put(d)
        self.multi_thread(3, dl)

    def walk(self):#遍历TED文件夹，找到所有的视频
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith('.mp4'):
                    self.video_list.append(name)

    def video_dl_list(self):#从数据库中找到所有视频下载链接，与已经存在的视频对比，输出需要下载的视频的URL
        query = "SELECT media_1500k FROM ted WHERE media_1500k != ''"
        self.cursor.execute(query)
        for (item,) in self.cursor:
            if not item.split('/')[-1] in self.video_list:
                print(item)
if __name__ == '__main__':
    ted = TED()
    ted.walk()
    ted.video_dl_list()
