import json
import sys
import bot
import datetime
import tzlocal

def build_records_from_json(filename, licensed):
    records = []

    jsonobj = json.load(open(filename))
    for e in jsonobj['entries']:
        e['license'] = licensed
    return jsonobj['entries']

def make_title(entryid, word):
    title = '%s (갈퀴 Django %d)' % (word, entryid)
    return title

def format_record(rec, datetimestr):
    assert('id' in rec)
    assert('word' in rec)
    assert('pos' in rec)

    title = make_title(rec['id'], rec['word'])

    lines = []
    lines += ['{{#set:갈퀴:라이선스=%s}}' % rec['license']]
    lines += ['{{#set:갈퀴:원본=갈퀴 Django}}']
    lines += ['{{#set:']
    lines += ['갈퀴 Django:가져온 시각=%s' % datetimestr]
    for k in sorted(rec.keys()):
        knames = {'contributors': '기여자',
                  'description': '설명',
                  'etym': '어원',
                  'id': '항목ID',
                  'license': '라이선스',
                  'orig': '본딧말',
                  'pos': '품사',
                  'props': '속성',
                  'stem': '어원',
                  'word': '표제어'}
        kname = knames[k]
        v = rec[k]
        if type(v) == int:
            lines += ['|갈퀴 Django:%s=%d' % (kname, v)]
        elif type(v) == str:
            lines += ['|갈퀴 Django:%s=%s' % (kname, v)]
        elif type(v) == list:
            for subv in v:
                lines += ['|갈퀴 Django:%s=%s' % (kname, subv)]
        else:
            raise Exception('No idea how to format ' + k)
    lines += ['}}']
    content = '\n'.join(lines)

    return title, content


def import_page(bot, title, content):
    #resp = bot.get(action='query', prop='revisions', titles=title, rvprop='content')
    #rev = list(resp['query']['pages'].keys())[0]

    content = '{{사전 항목}}\n' + content

    token = bot.get_edit_token();
    resp = bot.post(action='edit', title=title, text=content, token=token)
    assert(resp['edit']['result'] == 'Success')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: %s <ccby.json> <mplgpllgpl.json>\n' % sys.argv[0])
        sys.exit(1)

    filename1 = sys.argv[1]
    filename2 = sys.argv[2]

    records = build_records_from_json(filename1, 'CC BY 4.0')
    records += build_records_from_json(filename2, 'MPL 1.1/GPL 2.0/LGPL 2.1')
    records.sort(key=lambda x: x['word'])

    botsession = bot.Bot()
    botsession.login()

    magic = 'IMPORT 갈퀴 Django'
    new_page_prefix = '{{사전 항목}}'
    tz = tzlocal.get_localzone()
    dt = tz.localize(datetime.datetime.now())
    datetimestr = dt.isoformat()

    for i, record in zip(range(0, len(records)), records):
        if i % 100 == 0:
            print('Progress: %d/%d' % (i, len(records)))
        title, content = format_record(record, datetimestr)
        botsession.insert_text(title, magic, content, new_page_prefix, False)
