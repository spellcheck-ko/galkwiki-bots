# bot utility

import botconfig
import mwapi

class BotSession(mwapi.session.Session):
    def __init__(self):
        super(BotSession, self).__init__(botconfig.url, user_agent='Galkwi Bot')
        self.edit_token = None

    def get_edit_token(self):
        if not self.edit_token:
            resp = self.get(action='query', meta='tokens')
            self.edit_token = resp['query']['tokens']['csrftoken']
        return self.edit_token

    def login(self):
        if botconfig.is_bot:
            token_doc = self.post(action='query', meta='tokens', type='login')
            login_token = token_doc['query']['tokens']['logintoken']
            resp = self.post(action="login",
                             lgname=botconfig.username, lgpassword=botconfig.password,
                             lgtoken=login_token)
            assert(resp['login']['result'] == 'Success')
        else:
            super(BotSession, self).login(botconfig.username, botconfig.password)
        # clear edit token
        self.edit_token = None
