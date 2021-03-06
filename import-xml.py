#!/usr/bin/env python3

import sys
import bot
import botconfig
import time

if botconfig.is_bot:
    print('Bot can\'t import; edit your botconfig.py')
    sys.exit(1)

BATCH = 500

sess = bot.Bot()
sess.login()

token = sess.get_edit_token()

filenames = sys.argv[1:]

for filename in filenames:
    print('%s...' % filename)
    files = {'xml': (filename, open(filename).read())}

    resp = sess.post(files, action='import', token=token)
    print('Imported %d (%s ...)' % (len(resp['import']), resp['import'][0]['title']))
