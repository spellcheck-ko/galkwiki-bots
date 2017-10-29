from bot import Bot
import sys
import json

def find_dict_and_save(bot, query, filename):
    entries = []
    pages = bot.get_matched_pages(query)
    count = 0
    for page in pages:
        props = pages.get_printouts(page)
        entry = {}
        entry['word'] = props['맞춤법 검사:표제어'][0]
        pos_list = props['맞춤법 검사:품사']
        pos = pos_list[0]
        if len(pos_list) > 1 and pos_list[1].startswith(pos):
            pos = pos_list[1]
        entry['pos'] = pos
        if props['맞춤법 검사:속성'] or props['맞춤법 검사:불규칙 활용']:
            entry['props'] = []
            entry['props'] += props['맞춤법 검사:속성']
            entry['props'] += props['맞춤법 검사:불규칙 활용']
        entries.append(entry)
        count += 1
        if count % 100 == 0:
            sys.stderr.write('count: %d (%s)\n' % (count, entry['word']))
    obj = {'entries': entries}
    fp = open(filename, 'w', encoding='utf-8')
    json.dump(obj, fp, ensure_ascii=False, indent=1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: %s <basename>' % sys.argv[0])
        sys.exit(1)

    basename = sys.argv[1]

    bot = Bot()
    #bot.login()

    query_fmt = '[[분류:맞춤법 검사 사전 항목]] [[사전:원본 라이선스::%s]]'
    query_fmt += '|?맞춤법 검사:표제어|?맞춤법 검사:품사|?맞춤법 검사:속성|?맞춤법 검사:불규칙 활용'
    query = query_fmt % 'MPL 1.1/GPL 2.0/LGPL 2.1'
    find_dict_and_save(bot, query, '%s-mplgpllgpl.json' % basename)
    query = query_fmt % 'CC BY-SA 2.0 KR'
    find_dict_and_save(bot, query, '%s-ccbysa.json' % basename)
    query = query_fmt % 'CC BY 4.0'
    find_dict_and_save(bot, query, '%s-ccby.json' % basename)
