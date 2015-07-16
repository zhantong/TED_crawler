import urllib.request
import json
import time
import codecs
import mysql.connector
import re
import collections


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
    #ted = []
    offset = 0
    url = 'http://api.ted.com/v1/talks.json?api-key=%s&limit=100&offset=%i&fields=photo_urls,media,media_profile_uris,speaker_ids,speakers,theme_ids,tags'
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
        print('dealing:%i/%i' %
              (j['talks'][0]['talk']['id'], j['counts']['total']))
        if j['counts']['this'] != 100:
            break
        offset += 100
        time.sleep(0.5)
    with codecs.open('ted_json', 'w', 'utf-8') as f:
        f.write(json.dumps(ted, ensure_ascii=False, sort_keys=True))


def test():
    cnx = mysql.connector.connect(
        user=db['user'], password=db['password'], database=db['database'])
    cursor = cnx.cursor()
#    insert = ("INSERT INTO ted "
#              "(id,event_id,name,native_language_code,description,published_at,recorded_at,released_at,slug,media_created_at,media_duration,media_id,media_slug,media_1500k,media_2500k,media_480p,photo_url,speaker_id,tags,has_subtitle_en,has_subtitle_zh_cn) "
#              "VALUES ('%(id)s','%(event_id)s','%(name)s','%(native_language_code)s','%(description)s','%(published_at)s','%(recorded_at)s','%(released_at)s','%(slug)s','%(media_created_at)s','%(media_duration)s','%(media_id)s','%(media_slug)s','%(media_1500k)s','%(media_2500k)s','%(media_480p)s','%(photo_url)s','%(speaker_id)s','%(tags)s','%(has_subtitle_en)i','%(has_subtitle_zh_cn)i')")
#    insert = ("INSERT INTO ted "
#              "(id,event_id,name,native_language_code,description,published_at,recorded_at,released_at,slug,media_created_at,media_duration,media_id,media_slug,media_1500k,media_2500k,media_480p,photo_url,speaker_id,tags,has_subtitle_en,has_subtitle_zh_cn) "
#              "VALUES (%(id)s,%(event_id)s,%(name)s,%(native_language_code)s,%(description)s,%(published_at)s,%(recorded_at)s,%(released_at)s,%(slug)s,%(media_created_at)s,%(media_duration)s,%(media_id)s,%(media_slug)s,%(media_1500k)s,%(media_2500k)s,%(media_480p)s,%(photo_url)s,%(speaker_id)s,%(tags)s,%(has_subtitle_en)i,%(has_subtitle_zh_cn)i)")
    insert = ("INSERT IGNORE INTO ted "
              "(id,event_id,name,native_language_code,description,published_at,recorded_at,released_at,slug,media_created_at,media_duration,media_id,media_slug,media_1500k,media_2500k,media_480p,photo_url,speaker_id,tags,has_subtitle_en,has_subtitle_zh_cn) "
              "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')")
    with codecs.open('ted_json', 'r', 'utf-8') as f:
        j = json.loads(f.read())
    for t in j:
        #    for t in ted:
        # t=collections.defaultdict(int,t)
        class Counter(dict):

            def __missing__(self, key):
                return ''
#        t=Counter(t)

        tags = ''
        try:
            #            if 'podcast-high-en' in t['media_profile_uris']['internal']:
            #                has_subtitle_en = 1
            #            else:
            #                has_subtitle_en = 0
            #            if 'podcast-high-zh-cn' in t['media_profile_uris']['internal']:
            #                has_subtitle_zh_cn = 1
            #            else:
            #                has_subtitle_zh_cn = 0
            for tag in t['tags']:
                tags = tags+tag+', '
            tags = tags[:-2]
            print(t['id'])
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
                #'media_created_at': t['media']['created_at'],
                #'media_duration': t['media']['duration'],
                #'media_id': t['media']['id'],
                #'media_slug': t['media']['slug'],
                #'media_1500k': t['media_profile_uris']['internal']['1500k']['uri'],
                #'media_2500k': t['media_profile_uris']['internal']['2500k']['uri'],
                #'media_480p': t['media_profile_uris']['internal']['podcast-high']['uri'],
                'photo_url': t['photo_urls'][1]['url'],
                'speaker_id': t['speaker_ids'][0],
                'tags': tags,
                #'has_subtitle_en': has_subtitle_en,
                #'has_subtitle_zh_cn': has_subtitle_zh_cn,
            }
            if t['media'] != None:
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
        # cursor.execute(insert%(t['id'],t['event_id'],t['name'],t['native_language_code'],t['description'],t['published_at'],t['recorded_at'],t['released_at'],t['slug'],t['media']['created_at'],t['media']['duration'],t['media']['id'],t['media']['slug'],t['media_profile_uris']['internal']['1500k'],t['media_profile_uris']['internal']['2500k'],t['media_profile_uris']['internal']['podcast-high'],t['photo_urls'][1]['url'],t['speaker_ids'][0],))
        cursor.execute(insert % (info['id'], info['event_id'], info['name'], info['native_language_code'], info['description'], info['published_at'], info['recorded_at'], info['released_at'], info['slug'], info['media_created_at'], info[
                       'media_duration'], info['media_id'], info['media_slug'], info['media_1500k'], info['media_2500k'], info['media_480p'], info['photo_url'], info['speaker_id'], info['tags'], info['has_subtitle_en'], info['has_subtitle_zh_cn']))
        # cursor.execute(insert,info)
    cnx.commit()
    cursor.close()
    cnx.close()
if __name__ == '__main__':
    # dl_from_api()
    test()
