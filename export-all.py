#!/usr/bin/env python3

import bot

BATCH = 100

sess = bot.Bot()
sess.login()

resp = sess.get(action='query', meta='siteinfo', siprop='namespaces')

namespaces = [v['id'] for v in resp['query']['namespaces'].values() if v['id'] >= 0]
titles = []

for ns_id in namespaces:
    if int(ns_id) < 0:
        continue
    if int(ns_id) == 0:
        continue
    try:
        resp = sess.get(action='query', list='allpages', apnamespace=ns_id, aplimit=10)
        titles += [k['title'] for k in resp['query']['allpages']]
        while 'continue' in resp:
            continuefrom = resp['continue']['apcontinue']
            resp = sess.get(action='query', list='allpages', apnamespace=ns_id, aplimit=10, apfrom=continuefrom)
            titles += [k['title'] for k in resp['query']['allpages']]
    except:
        print('got exception on ns %s' % ns_id)
        assert(False)

for begin in range(0, len(titles), BATCH):
    end = begin + BATCH if (begin + BATCH) < len(titles) else len(titles)
    resp = sess.post(action='query', export=1, titles='|'.join(titles[begin:end]))
    open('export-%08d.xml' % begin, 'w').write(resp['query']['export']['*'])
