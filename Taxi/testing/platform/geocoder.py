# encoding: utf-8

#Geocoder API instructions
#https://a.yandex-team.ru/arc_vcs/extsearch/geo

import argparse
import requests


class PlatformEnv:

    def __init__(self, host):
        self._host = host

    def get_address(self, url):
        res = requests.get(self._host,
             params={'balancertimeout': 300000,
                     'gta': 'kind',
                     'gta': 'll',
                     'lang': 'ru',
                     'ms': 'pb',
                     'origin': 'yandex.taxi.logistic',
                     'reqid': '1645114083757424-1715335017-taxi-logistic-platform-stable-6-SAASQUERY',
                     'timeout': 5000000,
                     'type': 'geo',
                     'text': '117648, Москва, микрорайон Северное Чертаново, к409с1, кв.29'})

        print("\nresponse headers: {0}\n".format(res.headers))
        print("response json: {0}\n".format(res._content))

        res.raise_for_status()


ENV = {
    'testing': PlatformEnv(
        host='http://addrs-testing.search.yandex.net/search/stable/yandsearch',
    ),
    #'production': PlatformEnv(
    #    host='http://addrs.yandex.ru:17140/yandsearch',
    #)
}

def main():
    parser = argparse.ArgumentParser(description='Swiss army axe for LP testing.')

    parser.add_argument('--env', type=str, choices=ENV.keys(), required=True, default='testing')
    parser.add_argument('--address', type=str, help='Enter your address', required=True)

    args = parser.parse_args()

    env = ENV[args.env]

    env.get_address(args.address)


if __name__ == "__main__": 
     
    main()
