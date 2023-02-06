# encoding: utf-8

import json
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open("yandexuids_and_uids") as f:
    yandexuids = map(json.loads, f.readlines()[:])

for row in yandexuids:
    yandexuid, uid = row['yandexuid'], row['uid']
    res = urllib.request.urlopen(
        "https://achievement-api-d0.wdevx.yandex.ru/api/v1/achievements/all?yandexuid={}".format(yandexuid),
        context=ctx).read()
    res = json.loads(res)
    if res['value']:
        print({**res['value'], **row})
