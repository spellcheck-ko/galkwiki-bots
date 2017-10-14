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

if __name__ == '__main__':
    b = Bot()
    b.login()
    resp = b.get(action='query', meta='siteinfo', siprop='namespaces')
    print(resp)
