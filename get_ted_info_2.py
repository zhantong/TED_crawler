import urllib.request
import json
import time
import codecs
import mysql.connector
import re


class Counter(dict):

    def __missing__(self, key):
        return ''


def default_factory():
    return 'default value'
db = {
    'user': 'root',
    'password': '123456',
    'database': 'ted'
}
api_key = 'pykzs7satj3sabhpnh6j39p5'

ted = []


def dl_from_api():
    offset = 0
    url = ('http://api.ted.com/v1/talks.json?api-key=%s'
           '&limit=100'
           '&offset=%i'
           '&fields=photo_urls,media,media_profile_uris,speaker_ids,speakers,theme_ids,tags')
    while 1:
        try:
            con = urllib.request.urlopen(
                url % (api_key, offset)).read().decode('utf-8')
        except Exception as e:
            print(e)
            continue
        j = json.loads(con)
        for item in j['talks']:
            ted.append(item['talk'])
        print('id begin with:%i' % j['talks'][0]['talk']['id'])
        if j['counts']['this'] != 100:
            break
        offset += 100
        time.sleep(0.5)
    with codecs.open('ted_json', 'w', 'utf-8') as f:
        f.write(json.dumps(ted, ensure_ascii=False, sort_keys=True))


def get_eng_info():
    cnx = mysql.connector.connect(
        user=db['user'], password=db['password'], database=db['database'])
    cursor = cnx.cursor()
    insert = ("INSERT IGNORE INTO ted "
              "(id,event_id,name,native_language_code,description,published_at,"
              "recorded_at,released_at,slug,media_created_at,media_duration,"
              "media_id,media_slug,media_1500k,media_2500k,media_480p,photo_url,"
              "speaker_id,tags,has_subtitle_en,has_subtitle_zh_cn) "
              "VALUES ('%(id)s','%(event_id)s','%(name)s','%(native_language_code)s',"
              "'%(description)s','%(published_at)s','%(recorded_at)s','%(released_at)s',"
              "'%(slug)s','%(media_created_at)s','%(media_duration)s','%(media_id)s',"
              "'%(media_slug)s','%(media_1500k)s','%(media_2500k)s','%(media_480p)s',"
              "'%(photo_url)s','%(speaker_id)s','%(tags)s','%(has_subtitle_en)s',"
              "'%(has_subtitle_zh_cn)s')")
    with codecs.open('ted_json', 'r', 'utf-8') as f:
        j = json.loads(f.read())
    for t in j:
        tags = ''
        try:
            for tag in t['tags']:
                tags = tags+tag+', '
            tags = tags[:-2]
            print('inserting id %s to database' % t['id'])
            info = {
                'id': t['id'],
                'event_id': t['event_id'],
                'name': re.escape(t['name']),
                'native_language_code': t['native_language_code'],
                'description': re.escape(t['description']),
                'published_at': t['published_at'],
                'recorded_at': t['recorded_at'],
                'released_at': t['released_at'],
                'slug': t['slug'],
                'photo_url': t['photo_urls'][1]['url'],
                'speaker_id': t['speaker_ids'][0],
                'tags': tags,
            }
            if t['media']:
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
            info = Counter(info)
        except KeyError as e:
            print('key error:', e)
        cursor.execute(insert % info)
    cnx.commit()
    cursor.close()
    cnx.close()
def get_chi_info():
    cnx = mysql.connector.connect(
        user=db['user'], password=db['password'], database=db['database'])
    cursor = cnx.cursor()
    offset = 0
    url = ('http://api.ted.com/v1/talks.json?api-key=%s'
           '&limit=100'
           '&offset=%i'
           '&language=zh-cn')
    update=("UPDATE ted SET name_zh_cn='%s',description_zh_cn='%s' WHERE id='%s'")
    while 1:
        try:
            con = urllib.request.urlopen(
                url % (api_key, offset)).read().decode('utf-8')
        except Exception as e:
            print(e)
            continue
        j = json.loads(con)
        for item in j['talks']:
            cursor.execute(update%(re.escape(item['talk']['name']),re.escape(item['talk']['description']),item['talk']['id']))
            print('updated id %i' % item['talk']['id'])
        if j['counts']['this'] != 100:
            break
        offset += 100
        time.sleep(0.5)
    cnx.commit()
    cursor.close()
    cnx.close()        
if __name__ == '__main__':
    dl_from_api()
    get_eng_info()
    get_chi_info()
