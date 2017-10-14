#!/usr/bin/env python3

import sys
import bot
import botconfig

if botconfig.is_bot:
    print('Bot can\'t import; edit your botconfig.py')
    sys.exit(1)

BATCH = 500

sess = bot.Bot()
sess.login()

token = sess.get_edit_token()

filenames = sys.argv[1:]

for filename in filenames:
    files = {'xml': (filename, open(filename).read())}
    resp = sess.post(files, action='import', token=token)
    print('%s: %d pages imported' % (filename, len(resp['import'])))
