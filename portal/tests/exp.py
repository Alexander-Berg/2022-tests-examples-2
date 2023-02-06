#!/usr/bin/env python3
# coding: utf-8
import requests
import json
from multiprocessing.dummy import Pool as ThreadPool


url_base = 'http://geohelper-dev.wdevx.yandex.ru/geohelper'
poi_groups_data = '{"poi":[{"group":"food","subgroups":["где поесть"]},{"group":"business-lunch","subgroups":["ресторан с бизнес-ланчем"]},{"group":"shops","subgroups":["магазины продуктов"]},{"group":"gaz","subgroups":["азс"]},{"group":"atm","subgroups":["банкоматы"]},{"group":"drugstore","subgroups":["аптеки"]}]}'

with_photo = 0
without_photo = 0
counter = 0

def main():
    urls = []
    with open('geohelper.log') as f:
    # with open('test.geohelper.log') as f:
        for line in f.readlines():
            location = line.strip().split(' ')[5]
            # location += '&blocks=poi&test-id=40874'
            # location += '&blocks=poi&favexp=1'
            # location += '&blocks=poi&test-id=40882'
            location += '&blocks=poi&favexp=2'
            # make_request(location)

            urls.append(location)

    pool = ThreadPool(20)
    results = pool.map(make_request, urls)
    pool.close()
    pool.join()

    print('with:', with_photo)
    print('without:', without_photo)


def parse_answer(answer):
    parsed = json.loads(answer)
    global with_photo, without_photo, counter
    for obj in parsed['fav']:
        if 'photo' in obj:
            # print(obj['photo'])
            with_photo += 1
        else:
            # print(None)
            without_photo +=1
    counter += 1
    if counter % 1000 == 0:
        counter = counter % 1000
        print('with:', with_photo, 'without:', without_photo)


def make_request(location):
    url = url_base + location
    result = requests.post(url, data=poi_groups_data.encode('utf-8'))
    if result.status_code == 200:
        return parse_answer(result.text.strip())
    else:
        print('status_code', result.status_code)
        return None


if __name__ == '__main__':
    main()