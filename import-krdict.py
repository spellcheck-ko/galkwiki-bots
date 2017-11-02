import sys
import xml.etree.ElementTree as ET
import bot
import datetime
import tzlocal

def build_records_from_xml(filename):
    records = []

    xml = ET.parse(filename)
    root = xml.getroot()

    tz = tzlocal.get_localzone()
    dt = tz.localize(datetime.datetime.now())
    datetimestr = dt.isoformat()

    entries = root.find('Lexicon').findall('LexicalEntry')
    for entry in entries:
        rec = {}
        rec['항목ID'] = entry.get('val')
        rec['가져온 시각'] = datetimestr
        for item in entry:
            if item.tag == 'feat':
                if item.get('att') == 'homonym_number':
                    rec['동형어 번호'] = item.get('val')
                elif item.get('att') == 'lexicalUnit':
                    rec['구분'] = item.get('val')
                elif item.get('att') == 'partOfSpeech':
                    rec['품사'] = item.get('val')
                elif item.get('att') == 'vocabularyLevel':
                    rec['어휘 등급'] = item.get('val')
                elif item.get('att') == 'subjectCategiory':
                    rec['의미 범주'] = item.get('val')
                elif item.get('att') == 'semanticCategory':
                    rec['주제 및 상황 범주'] = item.get('val')
                elif item.get('att') == 'origin':
                    rec['원어'] = item.get('val')
                elif item.get('att') == 'annotation':
                    rec['전체 참고'] = item.get('val')
                else:
                    raise Exception('Unknown att ' + item.get('att'))
            elif item.tag == 'Lemma':
                for subitem in item:
                    if subitem.get('att') == 'writtenForm':
                        rec['표제어'] = subitem.get('val')
                    elif subitem.get('att') == 'variant':
                        rec['검색용 이형태'] = subitem.get('val')
                    else:
                        raise Exception('Unknown att ' + subitem.get('att'))
            elif item.tag == 'WordForm':
                type = [x.get('val') for x in item if x.get('att') == 'type'][0]
                if type == '발음':
                    if '발음' not in rec:
                        rec['발음'] = []
                    subrec = {}
                    for subitem in item:
                        if subitem.get('att') == 'type':
                            pass
                        elif subitem.get('att') == 'pronunciation':
                            if subitem.get('val'):
                                subrec['발음'] = subitem.get('val')
                            else:
                                subrec['발음'] = ''
                        elif subitem.get('att') == 'sound':
                            subrec['URL'] = subitem.get('val')
                        else:
                            raise Exception('Unknown att ' + subitem.get('att'))
                    rec['발음'].append(subrec)
                elif type == '활용':
                    if '활용' not in rec:
                        rec['활용'] = []
                    subrec = {}
                    for subitem in item:
                        if subitem.tag == 'feat':
                            if subitem.get('att') == 'type':
                                pass
                            elif subitem.get('att') == 'writtenForm':
                                if subitem.get('val'):
                                    subrec['형태'] = subitem.get('val')
                                else:
                                    subrec['형태'] = ''
                            elif subitem.get('att') == 'pronunciation':
                                pass
                                # FIXME - 사용하지않는 데이터이므로 일단 무시
                                # subrec['발음'] = subitem.get('val')
                            elif subitem.get('att') == 'sound':
                                pass
                                # FIXME - 사용하지않는 데이터이므로 일단 무시
                                # subrec['URL'] = subitem.get('val')
                            else:
                                raise Exception('Unknown att ' + subitem.get('att'))
                        elif subitem.tag == 'FormRepresentation':
                            pass
                            # FIXME - 사용하지않는 데이터이므로 일단 무시
                            # subsubrec = {}
                            # for subsubitem in subitem:
                            #     if subsubitem.get('att') == 'type':
                            #         frtype = subsubitem.get('val')
                            #     elif subsubitem.get('att') == 'writtenForm':
                            #         if subsubitem.get('val'):
                            #             subsubrec['형태'] = subsubitem.get('val')
                            #         else:
                            #             subsubrec['형태'] = ''
                            #     elif subsubitem.get('att') == 'pronunciation':
                            #         subsubrec['발음'] = subsubitem.get('val')
                            #     elif subsubitem.get('att') == 'sound':
                            #         subsubrec['URL'] = subsubitem.get('val')
                            #     else:
                            #         raise Exception('Unknown att ' + subitem.get('att'))
                            # subrec[frtype] = subsubrec
                        else:
                            raise Exception('Unknown tag ' + subitem.tag)
                    rec['활용'].append(subrec)
                else:
                    raise Exception('Unknown WordForm type ' + type)
            elif item.tag == 'Sense':
                sense = {}
                sense['의미ID'] = item.get('val')
                for subitem in item:
                    if subitem.tag == 'feat':
                        if subitem.get('att') == 'annotation':
                            sense['의미 참고'] = subitem.get('val')
                        elif subitem.get('att') == 'definition':
                            sense['뜻풀이'] = subitem.get('val')
                        elif subitem.get('att') == 'syntacticAnnotation':
                            sense['문형 참고'] = subitem.get('val')
                        elif subitem.get('att') == 'syntacticPattern':
                            sense['문형'] = subitem.get('val')
                        else:
                            raise Exception('Unknown att ' + subitem.get('att'))
                    elif subitem.tag == 'SenseRelation':
                        subsense = {}
                        subsensetype = ''
                        for subsubitem in subitem:
                            if subsubitem.get('att') == 'type':
                                subsensetype = subsubitem.get('val')
                            elif subsubitem.get('att') == 'id':
                                if subsubitem.get('val'):
                                    subsense['항목ID'] = subsubitem.get('val')
                            elif subsubitem.get('att') == 'lemma':
                                if subsubitem.get('val'):
                                    subsense['표제어'] = subsubitem.get('val')
                            elif subsubitem.get('att') == 'homonymNumber':
                                if subsubitem.get('val'):
                                    subsense['동형어 번호'] = subsubitem.get('val')
                            else:
                                raise Exception('Unknown att ' + subsubitem.get('att'))
                        # 내용이 없는 SenseRelation tag가 있으니 내용 여부 확인
                        if subsense:
                            if '관련어:' + subsensetype not in sense:
                                sense['관련어:' + subsensetype] = []
                            sense['관련어:' + subsensetype].append(subsense)
                    elif subitem.tag == 'SenseExample':
                        subtype, example = '', ''
                        for subsubitem in subitem:
                            if subsubitem.get('att') == 'type':
                                subtype = subsubitem.get('val')
                            elif subsubitem.get('att') == 'example':
                                example = subsubitem.get('val')
                            else:
                                raise Exception('Unknown att ' + subitem.get('att'))
                        if subtype == '1':
                            tt = '용례'
                        else:
                            tt = '용례:' + subtype
                        if tt not in sense:
                            sense[tt] = []
                        sense[tt].append(example)
                    elif subitem.tag == 'Multimedia':
                        subtype = ''
                        subsense = {}
                        for subsubitem in subitem:
                            if subsubitem.get('att') == 'type':
                                subtype = subsubitem.get('val')
                            elif subsubitem.get('att') == 'label':
                                subsense['레이블'] = subsubitem.get('val')
                            elif subsubitem.get('att') == 'url':
                                subsense['URL'] = subsubitem.get('val')
                            else:
                                raise Exception('Unknown att ' + subitem.get('att'))
                        if '다중 매체 정보:' + subtype not in sense:
                            sense['다중 매체 정보:' + subtype] = []
                        sense['다중 매체 정보:' + subtype].append(subsense)
                    else:
                        raise Exception('Unknown subitem tag ' + subitem.tag)
                if '의미' not in rec:
                    rec['의미'] = {}
                rec['의미'][sense['의미ID']] = sense
        records.append(rec)
    return records

def make_title(entryid, written, homonym='0'):
    if int(homonym) > 0:
        label = '%s (%03d)' % (written, int(homonym))
    else:
        label = written
    label = label.replace('[','❲').replace(']','❳')
    title = '%s (한국어기초사전 %s)' % (label, entryid)
    return title

def format_record(rec):
    assert('표제어' in rec)
    assert('항목ID' in rec)

    if '동형어 번호' in rec and int(rec['동형어 번호']) > 0:
        title = make_title(rec['항목ID'], rec['표제어'], rec['동형어 번호'])
    else:
        title = make_title(rec['항목ID'], rec['표제어'])

    lines = []
    lines += ['{{#set:사전:원본 라이선스=CC BY-SA 2.0 KR}}']
    lines += ['{{#set:사전:원본=한국어기초사전}}']
    lines += ['{{#set:']
    for k in sorted(rec.keys()):
        v = rec[k]
        if type(v) == str:
            lines += ['|한국어기초사전:%s=%s' % (k, v)]
        elif type(v) == list:
            for subv in v:
                if k == '활용':
                    if not subv['형태']:
                        continue
                    subv = subv['형태']
                    # url = subv['URL'] if 'URL' in subv else ''
                    # pron = subv['발음'] if '발음' in subv else ''
                    # subv = subv['형태'] + ';' + pron + ';' + url
                elif k == '발음':
                    url = subv['URL'] if 'URL' in subv else ''
                    if not url and not subv['발음']:
                        continue
                    subv = subv['발음'] + ';' + url
                lines += ['|한국어기초사전:%s=%s' % (k, subv)]
        elif k == '의미':
            pass
        else:
            raise Exception('No idea how to format ' + k)
    lines += ['}}']

    senses = rec['의미'] if '의미' in rec else {}
    for senseid in sorted(senses.keys()):
        sense = senses[senseid]
        lines += ['{{#subobject:%s' % senseid]
        for k in sorted(sense.keys()):
            v = sense[k]

            if type(v) == str:
                lines += ['|한국어기초사전:%s=%s' % (k, v)]
            elif k.startswith('관련어'):
                for subv in v:
                    s = make_title(subv['항목ID'], subv['표제어'], subv['동형어 번호'])
                    lines += ['|한국어기초사전:%s=%s' % (k, s)]
            elif k.startswith('용례'):
                for subv in v:
                    lines += ['|한국어기초사전:%s=%s' % (k, subv)]
            elif k.startswith('다중 매체 정보'):
                for subv in v:
                    s = '%s;%s' % (subv['레이블'], subv['URL'])
                    lines += ['|한국어기초사전:%s=%s' % (k, s)]
            else:
                raise Exception('No idea how to format ' + k)
        lines += ['}}']

    content = '\n'.join(lines)
    return title, content


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: %s <filename>...\n' % sys.argv[0])
        sys.exit(1)

    filenames = sys.argv[1:]

    records = []
    for filename in filenames:
        records += build_records_from_xml(filename)

    botsession = bot.Bot()
    botsession.login()

    magic = 'IMPORT 한국어기초사전'
    new_page_prefix = '{{사전 항목}}'

    for i, record in zip(range(0, len(records)), records):
        if i % 100 == 0:
            print('Progress: %d/%d' % (i, len(records)))

        title, content = format_record(record)

        botsession.insert_text(title, magic, content, new_page_prefix)
