import sys
import bot

b = bot.Bot()
b.login()

query = '[[사전:원본::갈퀴 Django]]'
pages = b.get_matched_pages(query)
stats = {'total':0,
         'found':0,
         'notfound':0,
         'unique':0,
         'multiple':0}
magic = '동일 단어 자동 검색'

for p in pages:
    props = b.get_properties(p)
    word = props['갈퀴_Django:표제어']
    pos_full = props['갈퀴_Django:품사']
    pos = pos_full.split(':')[0]

    if pos == '동사':
        pos += '||보조 동사'
    elif pos == '형용사':
        pos += '||보조 형용사'
    elif pos == '명사':
        pos += '||의존 명사'
        if word.endswith('적'):
            pos += '||관형사'

    # query the same words in 한국어기초사전
    q = '[[한국어기초사전:표제어::%s]] [[한국어기초사전:품사::%s]]' % (word, pos)
    resp = b.get(action='ask', query=q)
    if resp['query']['results']:
        stats['found'] += 1
        matched_pages = list(resp['query']['results'].keys())
        if len(matched_pages) > 1:
            stats['multiple'] += 1

            #q = '[[갈퀴_Django:표제어::%s]][[갈퀴_Django:품사::%s]]' % (word,pos)
            q = '[[갈퀴_Django:표제어::%s]]' % word
            resp = b.get(action='ask', query=q)
            if len(resp['query']['results'].keys()) > 1:
                # M:N
                propname = '사전:동일 단어 미확정'
            else:
                # 1:N
                propname = '사전:동일 단어'

            content = '\n'.join(['{{#set:%s=%s}}' % (propname, pp)
                                 for pp in matched_pages])
            b.insert_text(p, magic, content)
            content = '{{#set:%s=%s}}' % (propname, p)
            for pp in matched_pages:
                b.insert_text(pp, magic, content)
        else:
            stats['unique'] += 1
            content = '{{#set:사전:동일 단어=%s}}' % matched_pages[0]
            b.insert_text(p, magic, content)
            content = '{{#set:사전:동일 단어=%s}}' % p
            b.insert_text(matched_pages[0], magic, content)
    else:
        stats['notfound'] += 1
    stats['total'] += 1

    if stats['total'] % 100 == 0:
        print('count: %d' % stats['total'])

    #if stats['total'] >= 100:
    #    break

for k in ['total', 'found', 'notfound', 'unique', 'multiple']:
    print('%s: %d' % (k, stats[k]))
