# bot utility

import requests
import botconfig

class Bot:
    def __init__(self, host=None):
        self.session = requests.Session()
        if not host:
            host = botconfig.url
        self.url = host + '/w/api.php'
        self.edit_token = None
        self.headers = {'User-Agent': 'Galkwi Bot'}

    def get(self, **params):
        return self.request('get', params)

    def post(self, files=None, **params):
        return self.request('post', params, files)

    def request(self, method, params, files=None):
        if method == 'post':
            data = params
            data['format'] = 'json'
            params = None
        else:
            data = None
            params = params
            params['format'] = 'json'

        resp = self.session.request(method, self.url, params=params,
                                    data=data, files=files,
                                    headers=self.headers)

        doc = resp.json()
        return doc

    def login(self):
        token_doc = self.post(action='query', meta='tokens', type='login')
        login_token = token_doc['query']['tokens']['logintoken']
        if botconfig.is_bot:
            resp = self.post(action="login",
                             lgname=botconfig.username, lgpassword=botconfig.password,
                             lgtoken=login_token)
            assert(resp['login']['result'] == 'Success')
        else:
            resp = self.post(action="clientlogin",
                             username=botconfig.username, password=botconfig.password,
                             logintoken=login_token, loginreturnurl="http://example.org/")
            assert(resp['clientlogin']['status'] == 'PASS')
        # clear edit token
        self.edit_token = None

    def get_edit_token(self):
        if not self.edit_token:
            resp = self.get(action='query', meta='tokens')
            self.edit_token = resp['query']['tokens']['csrftoken']
        return self.edit_token

    def get_page_text(self, title):
        resp = self.get(action='query', prop='revisions', titles=title, rvprop='content')
        rev = list(resp['query']['pages'].keys())[0]
        if int(rev) < 0:
            return ''
        else:
            content = resp['query']['pages'][rev]['revisions'][0]['*']
            return content

    def replace_text_begin_end(self, content, magic, bit, new_page_prefix=''):
        begin_line = '<!-- BEGIN %s -->' % magic
        end_line = '<!-- END %s -->' % magic
        if content:
            a = content.find(begin_line)
            b = content.find(end_line)
            if a >= 0 and b >= 0:
                text_above = content[:a]
                text_below = content[b + len(end_line):]
            elif a < 0 and b < 0:
                text_above = content
                text_below = ''
            else:
                raise Exception('Wrong begin/end marks')
        else:
            text_above = new_page_prefix
            text_below = ''

        text_above = text_above.strip('\n')
        bit = bit.strip('\n')

        lines = []
        if text_above:
            lines.append(text_above)
        lines.append(begin_line)
        lines.append(bit)
        lines.append(end_line)
        if text_below:
            lines.append(text_below)

        return '\n'.join(lines)

    def insert_text(self, title, magic, bit, new_page_prefix='', dry_run=False):
        content = self.get_page_text(title)
        new_text = self.replace_text_begin_end(content, magic, bit, new_page_prefix)
        if dry_run:
            print(new_text)
            return

        token = self.get_edit_token();
        resp = self.post(action='edit', title=title, text=new_text, token=token)
        assert(resp['edit']['result'] == 'Success')


if __name__ == '__main__':
    b = Bot()
    b.login()
    resp = b.get(action='query', meta='siteinfo', siprop='namespaces')
    print(resp)
