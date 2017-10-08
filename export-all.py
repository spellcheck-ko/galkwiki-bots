#!/usr/bin/env python3

import mwapi

BOT_USERNAME = 'Admin@ImportBot'
BOT_PASSWORD = '1m5h6q6nqgh8ihss420st8lt2hd01l8o'
BATCH = 10000

sess = mwapi.Session('http://localhost:8080', user_agent='Test Bot')

token_doc = sess.post(action='query', meta='tokens', type='login')
login_token = token_doc['query']['tokens']['logintoken']
resp = sess.post(action="login", lgname=BOT_USERNAME, lgpassword=BOT_PASSWORD,
                 lgtoken=login_token)
assert(resp['login']['result'] == 'Success')
#resp = sess.login(username=BOT_USERNAME, password=BOT_PASSWORD)

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
    resp = sess.get(action='query', export=1, titles='|'.join(titles[begin:end]))
    open('export-%08d.xml' % begin, 'w').write(resp['query']['export']['*'])
