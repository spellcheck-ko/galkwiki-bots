#!/usr/bin/env python3

import sys
import datetime
import re

import xlrd
import hypua2jamo
import bot

BOT_USERNAME = 'Admin@ImportBot'
BOT_PASSWORD = '1m5h6q6nqgh8ihss420st8lt2hd01l8o'

class records_from_xls:
    def __init__(self, filename):
        workbook = xlrd.open_workbook(filename)
        self.sheet = workbook.sheet_by_index(0)
        self.nrows = self.sheet.nrows
        self.keys = self.sheet.row_values(0)
        self.i = 1

    def __len__(self):
        return self.nrows - 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < self.nrows:
            i = self.i
            self.i += 1
            values = self.sheet.row_values(i)
            return [(k,v) for k,v in zip(self.keys, values) if v != '']
        else:
            raise StopIteration()


def decode_string(s):
    # 한양 PUA
    s = hypua2jamo.translate(s)
    # 우리말샘 사이트 웹폰트
    while True:
        m = re.search('(?:<span class="korean-webfont">|<equ>)(&#x[0-9A-F]{1,6};|.)(?:</span>|</equ>)?', s)
        if not m:
            break
        ch = m.group(1)
        pua_map = {
            '\uE01D': '\u0254\u0342', # ɔ͂
            '\uE01E': '\u025B\u0342', # ɛ͂
            '\uE01F': 'n\u0304', # n̄
            '\uE020': '𝆑𝆑𝆑',
            '\uE021': '𝆑𝆑',
            '\uE022': '𝆑𝆏',
            '\uE023': '𝆑𝆎',
            '\uE024': '▞',
            '\uE025': '▚',
            '\uE026': '\u3001', # IDEOGRAPHIC COMMA
            '\uE02C': 'ᅟᅵᇰ',
            '\uE02E': '타ᇦ'
        }

        if ch.startswith('&#x') and ch.endswith(';'):
            ch = chr(int(ch[3:-1], 16))

        if ord(ch) in range(0xE000, 0xF8FF + 1) or ord(ch) in range(0xF0000, 0xFFFFD + 1) or ord(ch) in range(0x100000, 0x10FFFD + 1):
            if ch in pua_map:
                ch = pua_map[ch]
            else:
                ch = '<webfont>U+%X</webfont>' % ord(ch)

        a,b = m.span(0)
        s = s[:a] + ch + s[b:]
    # TODO: 기타 PUA
    return s


def escape_title(s):
    s = s.replace('[','(').replace(']',')')
    return s

def escape_value(s):
    s = s.replace('[','❲').replace(']','❳').replace('|','❘')
    s = s.replace('<', '❬').replace('>', '❭')
    return s

def get_record(rawrec):
    rec = []
    for (key,value) in rawrec:
        value = decode_string(value)
        if key == '발음':
            if value[0] == '[' and value[-1] == ']':
                value = value[1:-1]
            rec.append((key,value))
        elif key == '품사':
            if '·' in value:
                subvalues = value.split('·')
                for sv in subvalues:
                    sv = {'감':'감탄사',
                          '관':'관형사',
                          '구':'구',
                          '대':'대명사',
                          '동':'동사',
                          '명':'명사',
                          '부':'부사',
                          '수':'수사',
                          '의명':'의존 명사',
                          '조':'조사',
                          '형':'형용사'}[sv]
                    rec.append((key,sv))
            else:
                rec.append((key,value))
        elif key == '관련 어휘':
            subvalues = value.split('\n')
            for sv in subvalues:
                for p in ('낮춤말', '높임말', '반대말', '본말', '비슷한말', '준말', '참고 어휘'):
                    if sv.startswith(p + ' '):
                        subkey = p
                        subsubvalues = sv[len(subkey)+1:].split(', ')
                        for ssv in subsubvalues:
                            rec.append((key + ':' + subkey, ssv))
                        break
                else:
                    subsubvalues = sv.split(', ')
                    for ssv in subsubvalues:
                        rec.append((key, ssv))
        elif key in ('용례'):
            subvalues = value.split('\n')
            for sv in subvalues:
                rec.append((key,sv))
        elif key == '검색용 이형태':
            subvalues = value.split(', ')
            for sv in subvalues:
                rec.append((key,sv))
        elif key == '문형':
            if value[0] == '【' and value[-1] == '】':
                value = value[1:-1]
            subvalues = value.split('】 【')
            for sv in subvalues:
                rec.append((key,sv))
        elif key == '전문 분야':
            if value[0] == '『' and value[-1] == '』':
                rec.append((key,value[1:-1]))
            else:
                print('%s?: %s' % (key,value))
        elif key == '규범 정보':
            items = value.split('\n유형 ')
            assert(items[0].startswith('유형 '))
            items[0] = items[0][len('유형 '):]

            for item in items:
                lines = item.split('\n')
                vtype = lines[0]
                vjohang = ''
                vseolmyeong = ''
                for line in lines[1:]:
                    if line.startswith('관련 조항 '):
                        vjohang = line[len('관련 조항 '):]
                    elif line.startswith('설명 '):
                        vseolmyeong = line[len('설명 '):]
                    else:
                        sys.stderr.write('알 수 없는 규범 정보 라인: %s\n' % line)
                        assert(False)
                subkey = key + ':' + vtype
                sv = '\n'.join([vjohang, vseolmyeong])
                rec.append((subkey, sv))
        elif key == '역사 정보':
            subvalues = value.split('\n\n')
            for sv in subvalues:
                rec.append((key,sv))
        elif key == '속담' or key == '관용구':
            subvalues = value.split('\n\n')
            bugprefix = (key + ' ') * len(subvalues)
            if subvalues[0].startswith(bugprefix):
                subvalues[0] = subvalues[0][len(bugprefix):]
            for sv in subvalues:
                rec.append((key,sv))
        elif key == '다중 매체(멀티미디어) 정보':
            lines = value.split('\n')
            for i in range(0, len(lines), 2):
                sv = '\n'.join(lines[i:i+2])
                rec.append((key,sv))
        else:
            rec.append((key,value))
    return rec


def format_record(rec, datestr):
    lines = ['{{#set:갈퀴:원본=우리말샘}}']
    lines.append('{{#set:')
    lines.append('우리말샘:가져온 시각=%s' % datestr)
    for k,v in rec:
        value = escape_value(v)
        if k.startswith('규범 정보'):
            value = ';'.join(value.split('\n'))
        elif k == '다중 매체(멀티미디어) 정보':
            value = ';'.join(value.split('\n'))
        lines.append('|우리말샘:%s=%s' % (k, value))
    lines.append('}}')
    return '\n'.join(lines)


def edit_page(api_session, title, text):
    resp = api_session.get(action='query', prop='revisions', titles=title, rvprop='content')
    rev = list(resp['query']['pages'].keys())[0]
    begin_line = '<!-- BEGIN IMPORT 우리말샘 -->'
    end_line = '<!-- END IMPORT 우리말샘 -->'

    text_above = ''
    text_below = ''
    new_import = False
    if int(rev) >= 0:
        content = resp['query']['pages'][rev]['revisions'][0]['*']
        a = content.find(begin_line)
        b = content.find(end_line)
        if a >= 0 and b >= 0:
            text_above = content[:a]
            text_below = content[b + len(end_line):]
        elif a < 0 and b < 0:
            text_above = content + '\n'
            text_below = ''
            new_import = True
        else:
            sys.stdout.write('Wrong begin/end marks in page \"%s\"\n' % title)
            assert(False)

    lines = []

    if text_above == '' and text_below == '':
        lines.append('{{사전 항목}}\n')
    else:
        lines.append(text_above)
        if not text_above.endswith('\n'):
            lines.append('\n')
    if new_import or '갈퀴:라이선스' not in text_above:
        lines.append('{{#set:갈퀴:라이선스=CC BY-SA 2.0 KR}}\n')
    lines.append(begin_line)
    if not text.startswith('\n'):
        lines.append('\n')
    lines.append(text)
    if not text.endswith('\n'):
        lines.append('\n')
    lines.append(end_line)
    if not text_below.startswith('\n'):
        lines.append('\n')
    lines.append(text_below)
    new_text = ''.join(lines)

    token = api_session.get_edit_token();
    resp = api_session.post(action='edit', title=title, text=new_text, token=token)


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.stderr.write('Usage: %s filename.xml <maxentries>\n' % sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]
    if len(sys.argv) >= 3:
        maxentries = int(sys.argv[2])
    else:
        maxentries = -1

    api_sess = bot.BotSession()

    api_sess.login();

    records = records_from_xls(filename)
    if maxentries < 0:
        maxentries = len(records)

    datestr = datetime.datetime.utcnow().isoformat() + 'Z'

    for rawrec in records:
        if maxentries > 0:
            maxentries -= 1
        else:
            break

        rec = get_record(rawrec)

        word = [v for k,v in rec if k == '어휘'][0]
        serial = [v for k,v in rec if k == '의미 번호'][0]
        title = '%s (%s)' % (word.replace('-','').replace('^',''), serial)

        title = escape_title(title)
        text = format_record(rec, datestr)

        edit_page(api_sess, title, text)

main()
